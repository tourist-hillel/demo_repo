from typing import Any

from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from user_account.forms import UserPermissionsForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import FormView
from django.http import HttpResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from events.signals import custom_signal

User = get_user_model()


class PermissionsManagementService:
    @staticmethod
    def update_user_permissions(user, permission_ids):
        user.user_permissions.clear()
        permissions = Permission.objects.filter(id__in=permission_ids)
        user.user_permissions.set(permissions)

class ManageUserPermissionsView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'permissions_management.html'
    form_class = UserPermissionsForm

    def test_func(self) -> bool | None:
        return self.request.user.has_perm('user_account.can_manage_users')

    def handle_no_permission(self):
        return HttpResponseForbidden('Have no access to requested page')

    def get_target_user(self):
        return get_object_or_404(User, id=self.kwargs['user_id'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.get_target_user(),
            'manager': self.request.user
        })
        return kwargs

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context['target_user'] = self.get_target_user()
        return context

    def get_success_url(self) -> str:
        return reverse_lazy('manage_permissions', kwargs={'user_id': self.kwargs['user_id']})

    def form_valid(self, form: Any):
        selected_permissions = form.cleaned_data.get('permissions', [])
        target_user = self.get_target_user()

        PermissionsManagementService.update_user_permissions(
            target_user,
            selected_permissions
        )
        custom_signal.send(sender=Permission, action='user_permissions_updated', user=self.request.user)
        return super().form_valid(form)
