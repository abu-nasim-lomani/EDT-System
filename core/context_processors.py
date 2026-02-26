# core/context_processors.py

from .models import Notification

def notifications_processor(request):
    """
    Adds unread_notifications_count and recent_notifications to the global template context
    for authenticated users.
    """
    if request.user.is_authenticated:
        # Get up to 5 unread notifications, or just latest 5 notifications
        recent = Notification.objects.filter(user=request.user).order_by('-created_at')[:7]
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {
            'recent_notifications': recent,
            'unread_notifications_count': unread_count,
        }
    return {
        'recent_notifications': [],
        'unread_notifications_count': 0,
    }
