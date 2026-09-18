from django.urls import path
from ws_chat.views import chat_main_page

urlpatterns = [
    path('room/<str:room_name>', chat_main_page, name='chat_page')
]
