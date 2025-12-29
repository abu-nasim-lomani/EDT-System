# chatbot/templatetags/chatbot_tags.py

from django import template
from core.utils import is_pm_user, is_sm_user

register = template.Library()


@register.filter
def can_use_chatbot(user):
    """Check if user can use the chatbot (PM or SM)"""
    if not user or not user.is_authenticated:
        return False
    return is_pm_user(user) or is_sm_user(user)

