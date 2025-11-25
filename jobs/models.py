from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date

class Job(models.Model):
    JOB_TYPES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
    ]
    
    JOB_ROLES = [
        ('frontend', 'Frontend Developer'),
        ('backend', 'Backend Developer'),
        ('fullstack', 'Full Stack Developer'),
        ('designer', 'UI/UX Designer'),
        ('data_scientist', 'Data Scientist'),
        ('project_manager', 'Project Manager'),
        ('marketing', 'Marketing Specialist'),
        ('sales', 'Sales Executive'),
        ('hr', 'HR Manager'),
        ('other', 'Other'),
    ]
    
    EDUCATION_LEVELS = [
        ('high_school', 'High School'),
        ('associate', 'Associate Degree'),
        ('bachelor', "Bachelor's Degree"),
        ('master', "Master's Degree"),
        ('phd', 'PhD'),
    ]
    
    EXPERIENCE_LEVELS = [
        ('fresher', 'Fresher'),
        ('1-2', '1-2 years'),
        ('3-5', '3-5 years'),
        ('5-10', '5-10 years'),
        ('10+', '10+ years'),
    ]
    
    JOB_LEVELS = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('lead', 'Lead'),
        ('manager', 'Manager'),
        ('executive', 'Executive'),
    ]
    
    SALARY_TYPES = [
        ('hourly', 'Hourly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    VACANCY_RANGES = [
        ('1', '1'),
        ('2-5', '2-5'),
        ('6-10', '6-10'),
        ('10+', '10+'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('closed', 'Closed'),
        ('draft', 'Draft'),
    ]

    # Employer relationship
    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='jobs',
        limit_choices_to={'user_type': 'employer'}
    )
    # Make company_name nullable in existing rows by providing a default and allowing blank.
    # This avoids interactive migration prompts and preserves existing data.
    company_name = models.CharField(max_length=255, default='', blank=True)

    # Required fields
    title = models.CharField(max_length=100)
    description = models.TextField(help_text="Minimum 50 characters")
    job_role = models.CharField(max_length=50, choices=JOB_ROLES)
    location = models.CharField(max_length=100)
    
    # Salary information
    min_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_type = models.CharField(max_length=20, choices=SALARY_TYPES)
    
    # Advanced information
    education = models.CharField(max_length=20, choices=EDUCATION_LEVELS)
    experience = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    vacancies = models.CharField(max_length=10, choices=VACANCY_RANGES)
    expiration_date = models.DateField()
    job_level = models.CharField(max_length=20, choices=JOB_LEVELS)
    
    # Optional fields
    tags = models.CharField(max_length=255, blank=True)
    responsibilities = models.TextField(blank=True)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-posted_at']
        indexes = [
            models.Index(fields=['-posted_at']),
            models.Index(fields=['employer', 'status']),
        ]

    def clean(self):
        """Custom validation"""
        errors = {}
        
        # Validate title
        if not self.title or not self.title.strip():
            errors['title'] = 'Job title cannot be empty.'
        elif len(self.title) > 100:
            errors['title'] = 'Job title cannot exceed 100 characters.'
            
        # Validate description
        if not self.description or not self.description.strip():
            errors['description'] = 'Job description cannot be empty.'
        elif len(self.description.strip()) < 50:
            errors['description'] = 'Description must be at least 50 characters.'
            
        # Validate location
        if not self.location or not self.location.strip():
            errors['location'] = 'Location cannot be empty.'
            
        # Validate salary
        if self.min_salary and self.max_salary:
            if self.min_salary < 0:
                errors['min_salary'] = 'Minimum salary cannot be negative.'
            if self.max_salary < 0:
                errors['max_salary'] = 'Maximum salary cannot be negative.'
            if self.min_salary > self.max_salary:
                errors['min_salary'] = 'Minimum salary cannot be greater than maximum salary.'
                
        # Validate expiration date
        if self.expiration_date:
            if self.expiration_date < date.today():
                errors['expiration_date'] = 'Deadline must be a future date.'
                
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Update status based on expiration date
        if self.expiration_date and self.expiration_date < date.today():
            self.status = 'expired'

        # Auto-fill company_name from the related employer or employer profile when missing.
        if not self.company_name or not str(self.company_name).strip():
            company = None
            try:
                company = getattr(self.employer, 'company_name', None) or getattr(self.employer, 'company', None)
            except Exception:
                company = None

            if not company:
                # Try common profile relation names (employerprofile, profile)
                try:
                    profile = getattr(self.employer, 'employerprofile', None) or getattr(self.employer, 'profile', None)
                    if profile:
                        company = getattr(profile, 'company_name', None) or getattr(profile, 'company', None)
                except Exception:
                    company = None

            if company:
                self.company_name = company

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.company_name}"
    
    @property
    def is_active(self):
        return self.status == 'active' and self.expiration_date >= date.today()
    
    @property
    def days_until_expiration(self):
        if self.expiration_date:
            delta = self.expiration_date - date.today()
            return delta.days
        return None
