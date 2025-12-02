from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class SavedCandidate(models.Model):
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
