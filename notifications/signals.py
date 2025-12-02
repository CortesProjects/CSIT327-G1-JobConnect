from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from jobs.models import JobApplication
from notifications.utils import notify_application_status_change


@receiver(pre_save, sender=JobApplication)
def detect_status_change(sender, instance, **kwargs):
    if instance.pk: 
        try:
            old_instance = JobApplication.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except JobApplication.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=JobApplication)
def notify_on_status_change(sender, instance, created, **kwargs):

    if not created and hasattr(instance, '_old_status'):
        old_status = instance._old_status
        new_status = instance.status
        
        if old_status != new_status and new_status in ['reviewed', 'interview', 'rejected', 'hired']:
            notify_application_status_change(instance.applicant, instance.job, new_status)
