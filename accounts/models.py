from django.db import models
from django.contrib.auth.models import AbstractUser
import os


def resume_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    new_filename = f'resume_{instance.user.id}{ext}'
    return os.path.join('applicant_resumes', new_filename)


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']
    EMAIL_FIELD = 'email'

    USER_TYPE_CHOICES = (
        ('applicant', 'Applicant'),
        ('employer', 'Employer'),
        ('admin', 'Admin') 
    )
    
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES, 
        default='applicant',
        verbose_name='User Type'
    )
    
    @property
    def full_name(self):
        parts = [self.first_name, self.last_name]
        return ' '.join(part for part in parts if part)
    
    def set_name_from_full_name(self, full_name):
        parts = [p for p in full_name.strip().split() if p]
        if not parts:
            self.first_name = ''
            self.last_name = ''
            return

        if len(parts) == 1:
            self.first_name = parts[0]
            self.last_name = ''
        else:
            self.first_name = parts[0]
            self.last_name = ' '.join(parts[1:])
    
    @property
    def profile(self):
        '''
        Returns the specific profile instance (Applicant or Employer) 
        based on the user_type. This simplifies template access.
        '''
        if self.user_type == 'applicant':
            return self.applicant_profile_rel 
        elif self.user_type == 'employer':
            return self.employer_profile_rel
        return None 
    
    def __str__(self):
        return self.email


class UserVerification(models.Model):
    """
    Tracks the administrative approval status for accounts requiring verification.
    Primarily used for Employers and their business permits.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='verification'
    )
    admin_verifier = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verifications_performed',
        limit_choices_to={'user_type': 'admin'}
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    verification_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp of the last status update'
    )
    notes = models.TextField(
        blank=True,
        help_text='Admin comments on the verification decision'
    )
    
    class Meta:
        verbose_name = 'User Verification'
        verbose_name_plural = 'User Verifications'
    
    def __str__(self):
        return f"{self.user.email} - {self.get_status_display()}"


class UserSocialLink(models.Model):
    """
    Handles social media links for all users (Applicants and Employers).
    Supports multivalued social links (e.g., multiple platforms per user).
    """
    PLATFORM_CHOICES = [
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('github', 'GitHub'),
        ('youtube', 'YouTube'),
        ('website', 'Website'),
        ('portfolio', 'Portfolio'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='social_links'
    )
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'platform']
        ordering = ['created_at']
        verbose_name = 'User Social Link'
        verbose_name_plural = 'User Social Links'
    
    def __str__(self):
        return f"{self.user.email} - {self.get_platform_display()}"
