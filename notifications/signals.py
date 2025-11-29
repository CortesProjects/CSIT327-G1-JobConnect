"""
Signals for automatic notification creation on model changes.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from jobs.models import JobApplication
from notifications.utils import notify_application_status_change


@receiver(pre_save, sender=JobApplication)
def detect_status_change(sender, instance, **kwargs):
    """
    Detect when application status changes and store old status for comparison.
    """
    if instance.pk:  # Only for existing instances
        try:
            old_instance = JobApplication.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except JobApplication.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=JobApplication)
def notify_on_status_change(sender, instance, created, **kwargs):
    """
    Send notification to applicant when their application status changes.
    """
    if not created and hasattr(instance, '_old_status'):
        old_status = instance._old_status
        new_status = instance.status
        
        # Only notify if status actually changed and is significant
        if old_status != new_status and new_status in ['reviewed', 'interview', 'rejected', 'hired']:
            notify_application_status_change(instance.applicant, instance.job, new_status)
