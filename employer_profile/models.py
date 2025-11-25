from django.db import models
from django.conf import settings


class EmployerProfile(models.Model):
    """Stores data specific to employers/companies."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        primary_key=True,
        related_name='employer_profile_rel' 
    )
    
    # --- Step 1: Company Info ---
    # Employer profiles store company-specific data only. Personal name fields
    # (first/middle/last) are not applicable to employers and were removed.
    company_name = models.CharField(max_length=255, blank=True, null=True)
    about_us = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='employer_documents/logos/', blank=True, null=True)
    location = models.JSONField(
        blank=True, 
        null=True, 
        default=dict,
        help_text='Structured location data, e.g. {"city":"Manila","country":"PH"}'
    )
    banner = models.ImageField(upload_to='employer_documents/banners/', blank=True, null=True)
    business_permit = models.FileField(upload_to='employer_documents/permits/', blank=True, null=True)

    # --- Step 2: Founding Info ---
    ORGANIZATION_CHOICES = [
        ('corp', 'Corporation'),
        ('llc', 'LLC'),
        ('solo', 'Sole Proprietorship')
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
        ('1-10', '1-10 Employees'),
        ('11-50', '11-50 Employees'),
        ('51+', '51+ Employees')
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

    # --- Step 3: Contact ---
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)

    # Setup tracking
    setup_step = models.IntegerField(default=1) 
    
    def __str__(self):
        return f"Employer Profile for {self.user.email}"
