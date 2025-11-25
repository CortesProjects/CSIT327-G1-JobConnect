from django.db import models
from django.contrib.auth.models import AbstractUser
import os


def resume_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    new_filename = f'resume_{instance.user.id}{ext}'
    return os.path.join('applicant_resumes', new_filename)


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    middle_name = models.CharField(max_length=150, blank=True, default='')
    
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
    is_verified = models.BooleanField(default=False)
    
    @property
    def full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(part for part in parts if part)
    
    def set_name_from_full_name(self, full_name):
        parts = [p for p in full_name.strip().split() if p]
        if not parts:
            self.first_name = ''
            self.middle_name = ''
            self.last_name = ''
            return

        if len(parts) == 1:
            self.first_name = parts[0]
            self.middle_name = ''
            self.last_name = ''
        elif len(parts) == 2:
            self.first_name = parts[0]
            self.middle_name = ''
            self.last_name = parts[1]
        else:
            self.first_name = parts[0]
            self.last_name = parts[-1]
            self.middle_name = ' '.join(parts[1:-1])
    
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
