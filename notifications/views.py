from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Notification


@login_required
@require_http_methods(["GET"])
def get_notifications(request):
    try:
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.shortcuts import redirect
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            elif request.user.is_staff or request.user.is_superuser:
                return redirect('dashboard:admin_dashboards')
            else:
                return redirect('dashboard:dashboard')
        
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:20] 

        notifications_data = []
        for notif in notifications:
            notifications_data.append({
                'id': notif.id,
                'type': notif.notification_type,
                'title': notif.title,
                'message': notif.message,
                'link': notif.link or '',
                'is_read': notif.is_read,
                'created_at': notif.created_at.isoformat(),
                'time_ago': get_time_ago(notif.created_at),
            })
        
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        return JsonResponse({
            'success': True,
            'notifications': notifications_data,
            'unread_count': unread_count,
        })
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in get_notifications: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Failed to fetch notifications',
            'notifications': [],
            'unread_count': 0,
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_unread_count(request):
    try:
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.shortcuts import redirect
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            elif request.user.is_staff or request.user.is_superuser:
                return redirect('dashboard:admin_dashboards')
            else:
                return redirect('dashboard:dashboard')
        
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({
            'success': True,
            'unread_count': unread_count,
        })
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in get_unread_count: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Failed to fetch unread count',
            'unread_count': 0,
        }, status=500)


@login_required
@require_http_methods(["POST"])
def mark_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.mark_as_read()
        
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read',
            'unread_count': unread_count,
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found',
        }, status=404)


@login_required
@require_http_methods(["POST"])
def mark_all_as_read(request):
    updated_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return JsonResponse({
        'success': True,
        'message': f'{updated_count} notification(s) marked as read',
        'unread_count': 0,
    })


@login_required
@require_http_methods(["POST"])
def delete_notification(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.delete()
        
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification deleted',
            'unread_count': unread_count,
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found',
        }, status=404)


def get_time_ago(dt):
    from django.utils import timezone
    
    now = timezone.now()
    diff = now - dt
    
    seconds = diff.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    
    if seconds < 60:
        return "Just now"
    elif minutes < 60:
        return f"{int(minutes)}m ago"
    elif hours < 24:
        return f"{int(hours)}h ago"
    elif days < 7:
        return f"{int(days)}d ago"
    elif days < 30:
        weeks = int(days / 7)
        return f"{weeks}w ago"
    else:
        months = int(days / 30)
        return f"{months}mo ago"
