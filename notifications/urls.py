from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.get_notifications, name='list'),
    path('unread-count/', views.get_unread_count, name='unread_count'),
    path('<int:notification_id>/mark-read/', views.mark_as_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_read'),
    path('<int:notification_id>/delete/', views.delete_notification, name='delete'),
]
