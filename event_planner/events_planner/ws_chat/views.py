from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from user_account.forms import EventUserForm
from django.contrib.auth import login


@login_required
def chat_main_page(request, room_name):
    return render(request, 'chat_main_page.html', {'room_name': room_name})


def register(request):
    if request.method == 'POST':
        form = EventUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat_page', room_name='guest_room')
    else:
        form = EventUserForm()
    return render(request, 'registration/register.html', {'form': form})


def test_view():
    return None
