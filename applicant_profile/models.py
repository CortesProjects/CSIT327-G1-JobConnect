from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator, FileExtensionValidator


class ApplicantProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        primary_key=True,
        related_name='applicant_profile_rel'
    )
    
    first_name = models.CharField(max_length=150, blank=True)
    middle_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    profile_image = models.ImageField(
        upload_to='applicant_documents/profile_images/',
        blank=True,
        null=True,
        help_text="Applicant's profile picture"
    )
    
    contact_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[MinLengthValidator(10, message="Contact number must be at least 10 digits.")],
        help_text="Applicant's contact phone number"
    )
    
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Professional title (e.g., 'Senior Frontend Developer')"
    )
    
    resume = models.FileField(
        upload_to='applicant_documents/resumes/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        blank=True,
        null=True,
        help_text="Resume/CV document (PDF, DOC, or DOCX)"
    )
    
    biography = models.TextField(
        blank=True,
        help_text="Brief 'About Me' or summary section"
    )
    
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text="For age verification or demographic data"
    )
    
    EDUCATION_LEVEL_CHOICES = [
        ('high_school', 'High School'),
        ('associate', 'Associate Degree'),
        ('bachelor', "Bachelor's Degree"),
        ('master', "Master's Degree"),
        ('doctorate', 'Doctorate/PhD'),
        ('vocational', 'Vocational/Technical'),
    ]
    education_level = models.CharField(
        max_length=20,
        choices=EDUCATION_LEVEL_CHOICES,
        blank=True,
        help_text="Highest education level attained"
    )
    
    experience =models.CharField(
        max_length=100,
        blank=True,
        choices=[
            ('0-1', '0-1 years'),
            ('1-3', '1-3 years'),
            ('3-5', '3-5 years'),
            ('5-10', '5-10 years'),
            ('10+', '10+ years'),
        ],
        help_text="Years of experience (e.g., '0-1 years', '2-5 years', '5+ years')"
    )
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('non_binary', 'Non-Binary'),
        ('prefer_not_to_say', 'Prefer Not to Say'),
    ]
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True,
        help_text="Gender identification"
    )
    
    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('prefer_not_to_say', 'Prefer Not to Say'),
    ]
    marital_status = models.CharField(
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        blank=True,
        help_text="Marital status information"
    )
    
    nationality = models.CharField(
        max_length=100,
        blank=True,
        help_text="Applicant's nationality"
    )
    
    location_street = models.CharField(
        max_length=255,
        blank=True,
        help_text="Street address"
    )
    location_city = models.CharField(
        max_length=100,
        blank=True,
        help_text="City of residence"
    )
    location_country = models.CharField(
        max_length=100,
        blank=True,
        help_text="Country of residence"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Automatically records the last time the profile was modified"
    )

    is_public = models.BooleanField(
        default=False,
        help_text="Whether the applicant profile is visible to employers/public"
    )
    
    class Meta:
        verbose_name = 'Applicant Profile'
        verbose_name_plural = 'Applicant Profiles'
        ordering = ['-updated_at']
    
    @property
    def full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(part for part in parts if part)
    
    @property
    def location(self):
        parts = [self.location_street, self.location_city, self.location_country]
        return ', '.join(part for part in parts if part)

    @property
    def education(self):
        """Human-readable education label for templates expecting `applicant.education`."""
        if self.education_level:
            try:
                return self.get_education_level_display()
            except Exception:
                return self.education_level
        return ''

    @property
    def is_complete(self):
        required = [self.first_name, self.last_name]
        additional = any([bool(self.profile_image), bool(self.resume), bool(self.contact_number)])
        return all(required) and additional

    @property
    def profile_image_url(self):
        try:
            if self.profile_image and hasattr(self.profile_image, 'url'):
                return self.profile_image.url
        except Exception:
            pass
        return '/media/defaults/default-avatar.png'
    
    def __str__(self):
        return f"{self.full_name or 'Unnamed'} ({self.user.email})"


class NotificationPreferences(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='notification_preferences'
    )
    
    notify_shortlisted = models.BooleanField(
        default=True,
        help_text="Notify when shortlisted by employers"
    )
    
    notify_applications = models.BooleanField(
        default=True,
        help_text="Notify when application status changes"
    )
    
    notify_job_alerts = models.BooleanField(
        default=True,
        help_text="Notify about new jobs matching job alert preferences"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"Notification preferences for {self.user.email}"
