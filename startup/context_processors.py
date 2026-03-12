from accounts.models import Notification


def notifications_context(request):
    """
    Inject unread notification count and recent notifications into every
    template rendered for authenticated users.
    """
    if request.user.is_authenticated:
        unread = request.user.notifications.filter(read=False)
        return {
            'notifications_count': unread.count(),
            'notifications': request.user.notifications.all().order_by('-created_at')[:20],
        }
    return {
        'notifications_count': 0,
        'notifications': [],
    }
