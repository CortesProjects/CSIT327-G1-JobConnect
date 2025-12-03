from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

User = get_user_model()


class SavedCandidate(models.Model):
    """Model to track candidates saved by employers for future reference"""
    employer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='saved_candidates',
        limit_choices_to={'user_type': 'employer'}
    )
    application = models.ForeignKey(
        'jobs.JobApplication',
        on_delete=models.CASCADE,
        related_name='saved_by_employers'
    )
    saved_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Private notes about this candidate")
    
    class Meta:
        unique_together = ('employer', 'application')
        ordering = ['-saved_at']
        indexes = [
            models.Index(fields=['employer', '-saved_at']),
        ]
    
    def __str__(self):
        return f"{self.employer.email} saved {self.application.applicant.email}"

class Conversation(models.Model):
    """
    Simple conversation between users. Participants is M2M so it can be extended later.
    """
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    subject = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.subject or f"Conversation {self.pk}"

    def other_participants(self, user):
        return self.participants.exclude(pk=user.pk)

    def other_participant(self, user):
        """Return a single other participant (useful for 1:1)."""
        return self.participants.exclude(pk=user.pk).first()

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    body = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    attachment = models.FileField(upload_to='message_attachments/', null=True, blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Msg {self.pk} in Conv {self.conversation_id} by {self.sender_id}"