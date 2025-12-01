from django.db import models
from django.conf import settings
from utils.managers import NotificationManager


class Notification(models.Model):
    """
    System notifications for users (job applications, status changes, etc.)
    """
    NOTIFICATION_TYPES = [
        ('application_received', 'Application Received'),
        ('application_status', 'Application Status Update'),
        ('application_shortlist', 'Application Shortlisted'),
        ('application_rejected', 'Application Rejected'),
        ('application_hired', 'Application Hired'),
        ('job_posted', 'Job Posted'),
        ('job_alert', 'Job Alert Match'),
        ('system', 'System Notification'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="User who will receive this notification"
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        default='system',
        help_text="Type of notification"
    )
    title = models.CharField(
        max_length=200,
        help_text="Notification title"
    )
    message = models.TextField(
        help_text="Notification message content"
    )
    link = models.CharField(
        max_length=500,
        blank=True,
        help_text="Optional link for this notification"
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Whether the user has read this notification"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this notification was created"
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this notification was read"
    )
    
    # Optional: Link to related objects
    related_job_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID of related job (if applicable)"
    )
    related_application_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID of related application (if applicable)"
    )
    
    # Custom manager with chainable queryset methods
    objects = NotificationManager()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"
    
    def mark_as_read(self):
        """Mark this notification as read."""
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
