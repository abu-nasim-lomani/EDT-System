# chatbot/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('message/', views.chat_message, name='chatbot_message'),
    path('conversations/', views.chat_conversations, name='chatbot_conversations'),
    path('new/', views.new_conversation, name='chatbot_new'),
]

