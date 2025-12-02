from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Resume(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='resumes',
        limit_choices_to={'user_type': 'applicant'}
    )
    name = models.CharField(max_length=255, help_text="Display name for this resume")
    file = models.FileField(upload_to='resumes/%Y/%m/', help_text="PDF, DOC, or DOCX file")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_default = models.BooleanField(default=False, help_text="Use this resume by default when applying")
    
    class Meta:
        ordering = ['-is_default', '-uploaded_at']
        verbose_name = 'Resume'
        verbose_name_plural = 'Resumes'
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    def save(self, *args, **kwargs):
        if self.is_default:
            Resume.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
