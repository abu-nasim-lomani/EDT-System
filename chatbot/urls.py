# chatbot/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_page, name='chatbot_page'),
    path('message/', views.chat_message, name='chatbot_message'),
    path('conversations/', views.chat_conversations, name='chatbot_conversations'),
    path('new/', views.new_conversation, name='chatbot_new'),
    path('stt/', views.stt_view, name='chatbot_stt'),
    path('tts/', views.tts_view, name='chatbot_tts'),
]
