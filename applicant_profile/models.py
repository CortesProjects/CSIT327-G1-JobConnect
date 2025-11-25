from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator


class ApplicantProfile(models.Model):
    """
    Stores all specific, detailed information about a job applicant.
    Linked to accounts.User via One-to-One relationship.
    Social links are stored in accounts.UserSocialLink.
    """
    
    # Core relationship
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        primary_key=True,
        related_name='applicant_profile_rel'
    )
    
    # Personal Information (Composite full name)
    first_name = models.CharField(max_length=150, blank=True)
    middle_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    # Profile Image
    profile_image = models.ImageField(
        upload_to='profile_images/applicant/',
        blank=True,
        null=True,
        help_text="Applicant's profile picture"
    )
    
    # Contact Information
    contact_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Applicant's contact phone number"
    )
    
    # Professional Information
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Professional title (e.g., 'Senior Frontend Developer')"
    )
    
    # Resume/CV
    resume = models.FileField(
        upload_to='applicant_documents/resumes/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        blank=True,
        null=True,
        help_text="Resume/CV document (PDF, DOC, or DOCX)"
    )
    
    # Biography
    biography = models.TextField(
        blank=True,
        help_text="Brief 'About Me' or summary section"
    )
    
    # Demographics
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
        ('phd', 'PhD'),
        ('other', 'Other'),
    ]
    education_level = models.CharField(
        max_length=20,
        choices=EDUCATION_LEVEL_CHOICES,
        blank=True,
        help_text="Highest education level attained"
    )
    
    years_of_experience = models.IntegerField(
        default=0,
        help_text="Total professional experience in years"
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
        blank=True
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
        blank=True
    )
    
    nationality = models.CharField(
        max_length=100,
        blank=True,
        help_text="Applicant's nationality"
    )
    
    # Location (Composite)
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
    
    # Metadata
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Automatically records the last time the profile was modified"
    )
    
    class Meta:
        verbose_name = 'Applicant Profile'
        verbose_name_plural = 'Applicant Profiles'
        ordering = ['-updated_at']
    
    @property
    def full_name(self):
        """Returns the complete name combining first, middle, and last name."""
        parts = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(part for part in parts if part)
    
    @property
    def location(self):
        """Returns formatted location string."""
        parts = [self.location_city, self.location_country]
        return ', '.join(part for part in parts if part)
    
    def __str__(self):
        return f"{self.full_name or 'Unnamed'} ({self.user.email})"
