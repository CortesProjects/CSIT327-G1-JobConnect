from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, FileExtensionValidator
import os

def resume_upload_path(instance, filename):
    """
    Generates a unique path for resume files: resumes/resume_{user_id}.ext
    """
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
    
    @property
    def full_name(self):
        """Returns the full name combining first, middle, and last name."""
        parts = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(part for part in parts if part)
    
    def set_name_from_full_name(self, full_name):
        """Parse full name and set first_name and last_name."""
        parts = full_name.strip().split(None, 1)  # Split on first space
        self.first_name = parts[0] if parts else ''
        self.last_name = parts[1] if len(parts) > 1 else ''
    
    @property
    def profile(self):
        """
        Returns the specific profile instance (Applicant or Employer) 
        based on the user_type. This simplifies template access.
        """
        if self.user_type == 'applicant':
            return self.applicant_profile_rel 
        elif self.user_type == 'employer':
            return self.employer_profile_rel
        return None 
    
    def __str__(self):
        return self.email


class ApplicantProfile(models.Model):
    """Stores data specific to applicants."""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        primary_key=True,
        related_name='applicant_profile_rel' 
    )
    
    image = models.ImageField(
        upload_to='profile_images/applicant/', 
        default='defaults/default-avatar.png', 
        null=True, 
        blank=True
    )
    setup_step_progress = models.IntegerField(default=1)
    
    # Step 1: Personal Info
    # Name fields (editable during profile setup)
    first_name = models.CharField(max_length=150, blank=True, default='')
    middle_name = models.CharField(max_length=150, blank=True, default='')
    last_name = models.CharField(max_length=150, blank=True, default='')
    
    contact_number = models.CharField(
        max_length=15, 
        validators=[MinLengthValidator(10, message="Contact number must be at least 10 digits.")],
        blank=True
    )
    location = models.CharField(
        max_length=255, 
        help_text="e.g., Cebu City, Philippines",
        blank=True
    )

    # Step 2: Education
    school_name = models.CharField(max_length=255, blank=True)
    degree = models.CharField(max_length=255, help_text="e.g., BS in Information Technology", blank=True)
    year_level = models.CharField(max_length=50, help_text="e.g., 3rd Year, Graduate", blank=True)

    # Step 3: Skills & Resume
    skills_summary = models.TextField(
        blank=True, 
        help_text="Comma-separated list of your key skills."
    )
    resume = models.FileField(
        upload_to='applicant_documents/resumes/',
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])
        ],
        help_text="PDF, DOC, or DOCX only. Max 5MB.",
        blank=True,
        null=True
    )

    # Profile Metadata
    profile_completeness = models.IntegerField(default=0)
    is_public = models.BooleanField(default=True, help_text="Allow employers to view your profile.")
    
    def calculate_completeness(self):
        """Calculates and updates the profile completion percentage."""
        total_fields = 6 # contact, location, school, degree, year, resume
        filled_fields = 0
        
        if self.contact_number: filled_fields += 1
        if self.location: filled_fields += 1
        if self.school_name: filled_fields += 1
        if self.degree: filled_fields += 1
        if self.year_level: filled_fields += 1
        if self.resume: filled_fields += 1
            
        self.profile_completeness = int((filled_fields / total_fields) * 100)
        self.save(update_fields=['profile_completeness'])
    
    def __str__(self):
        return f"Applicant Profile for {self.user.email}"

# ... (Your EmployerProfile model remains unchanged) ...
class EmployerProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        primary_key=True,
        related_name='employer_profile_rel' 
    )
    
    # --- Step 1: Company Info (Existing Fields) ---
    # DEPRECATED: Name fields are not used for employer profiles (company_name is used instead)
    # Kept for backwards compatibility - can be removed in future migration
    first_name = models.CharField(max_length=150, blank=True, default='')
    middle_name = models.CharField(max_length=150, blank=True, default='')
    last_name = models.CharField(max_length=150, blank=True, default='')
    
    company_name = models.CharField(max_length=255, blank=True, null=True)
    about_us = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='employer_documents/logos/', blank=True, null=True)
    business_permit = models.FileField(upload_to='employer_documents/permits/', blank=True, null=True)

    # --- Step 2: Founding Info (NEW FIELDS) ---
    ORGANIZATION_CHOICES = [
        ('corp', 'Corporation'), ('llc', 'LLC'), ('solo', 'Sole Proprietorship')
    ]
    INDUSTRY_CHOICES = [
        ('tech', 'Technology'), 
        ('finance', 'Finance'), 
        ('health', 'Healthcare'),
        ('retail', 'Retail'),
        ('manu', 'Manufacturing'),
        ('edu', 'Education'),
        ('nonprofit', 'Non-Profit'),
        ('construction', 'Construction'),
        ('other', 'Other'),
    ]
    TEAM_SIZE_CHOICES = [
        ('1-10', '1-10 Employees'), ('11-50', '11-50 Employees'), ('51+', '51+ Employees')
    ]
    
    organization_type = models.CharField(max_length=50, choices=ORGANIZATION_CHOICES, blank=True, null=True)
    industry_type = models.CharField(
        max_length=50, 
        choices=INDUSTRY_CHOICES, 
        blank=True, 
        null=True
    )
    team_size = models.CharField(max_length=20, choices=TEAM_SIZE_CHOICES, blank=True, null=True)
    year_established = models.DateField(blank=True, null=True)
    company_website = models.URLField(max_length=200, blank=True, null=True)
    company_vision = models.TextField(blank=True, null=True)

    # --- Step 3: Contact (NEW FIELDS) ---
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)

    setup_step = models.IntegerField(default=1) 
    
    def __str__(self):
        return f"Employer Profile for {self.user.email}"