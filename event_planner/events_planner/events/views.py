from typing import Any
import logging
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponseForbidden, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import View, ContextMixin, TemplateResponseMixin
from django.views.generic import ListView
from events.models import Event
from events.forms import EventSearchForm, EventForm
from events.mixins import FormMixn, CacheViewMixin
from events.tasks import log_new_event


logger = logging.getLogger(__name__)

@login_required
def events_list(request):
    # breakpoint()
    # import pdb; pdb.set_trace()
    logger.info(f'Search with params: {request.GET}')
    search_form = EventSearchForm(request.GET or None)


    events = Event.objecs.filter(user=request.user)
    if request.user.is_superuser:
        logger.warning(f'Access by SU: {request.user}')
        events = Event.objects.all()

    if search_form.is_valid():
        search_title = search_form.cleaned_data.get('title')
        if search_title:
            events = events.filter(title__icontains=search_title)
    else:
        logger.error('form validation error')
    return render(request, 'events_list.html', {'events': events, 'search_form': search_form})


class TestView(CacheViewMixin, ContextMixin, TemplateResponseMixin, View):
    extra_context = {'site_name': 'Hillel'}
    template_name = 'events_list.html'
    cache_timeout = 60
    cache_timeout_authenticated = 0

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        events = Event.objects.all()
        context['events'] = events
        return self.render_to_response({'events': events})


class EventsList(PermissionRequiredMixin, CacheViewMixin, FormMixn, ListView):
    model = Event
    # queryset = Event.objects.filter(is_completed=False)
    template_name = 'events_list.html'
    context_object_name = 'events'
    form = EventSearchForm
    raise_exception = True
    cache_timeout = 60*2
    cache_timeout_authenticated = 40
    permission_required = 'events.view_event'


class AdminEventsList(LoginRequiredMixin, EventsList):
    def get_queryset(self) -> QuerySet[Any]:

        events = Event.objects.filter(user=self.request.user)
        if self.request.user.is_superuser:
            events = Event.objects.all()
        form = self.form(self.request.GET or None)

        if form.is_valid():
            search_title = form.cleaned_data.get('title')
            if search_title:
                events = events.filter(title__icontains=search_title)
        return events


@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    is_author = event.user == request.user
    if not any([is_author, request.user.is_superuser]):
        raise Http404(f'Not allowed. User {request.user} has no permits to view this page')
    return render(request, 'event_details.html', {'event': event})


@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, user=request.user)
        if form.is_valid():
            event = form.save()
            log_new_event.delay(event.pk)
            return redirect('events_list')
    else:
        form = EventForm(user=request.user)
    return render(request, 'event_form.html', {'form': form})


@login_required
def event_edit(request, event_id):
    event = get_object_or_404(Event, id=event_id, user=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('events_list')
    else:
        form = EventForm(instance=event, user=request.user)
    return render(request, 'event_form.html', {'form': form})

