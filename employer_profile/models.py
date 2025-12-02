from django.db import models
from django.conf import settings


class EmployerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        primary_key=True,
        related_name='employer_profile_rel'
    )
    
    company_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Legal or trade name of the company"
    )
    
    company_profile_image = models.ImageField(
        upload_to='employer_documents/logos/',
        blank=True,
        null=True,
        help_text="Company logo"
    )
    
    company_banner_image = models.ImageField(
        upload_to='employer_documents/banners/',
        blank=True,
        null=True,
        help_text="Large banner image for company profile page"
    )
    
    company_business_permit = models.FileField(
        upload_to='employer_documents/permits/',
        blank=True,
        null=True,
        help_text="Required business registration document for admin verification"
    )
    
    # Company Description
    about_us = models.TextField(
        blank=True, 
        null= True,
        help_text="Detailed description of company's mission, culture, etc."
    )
    
    # Organization Details
    ORGANIZATION_CHOICES = [
        ('corp', 'Corporation'),
        ('llc', 'LLC'),
        ('solo', 'Sole Proprietorship')
    ]
    
    organization_type = models.CharField(
        max_length=50,
        choices=ORGANIZATION_CHOICES,
        blank=True,
        help_text="Type of organization"
    )

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

    industry_type = models.CharField(
        max_length=100,
        blank=True,
        choices=INDUSTRY_CHOICES,
        help_text="E.g., Technology, Healthcare, Finance, Manufacturing"
    )

    TEAM_SIZE_CHOICES = [
        ('1-10', '1-10 Employees'),
        ('11-50', '11-50 Employees'),
        ('51+', '51+ Employees')
    ]
    
    team_size = models.CharField(
        max_length=20, 
        choices=TEAM_SIZE_CHOICES, 
        blank=True,
        help_text="Number of employees"
    )
    
    year_established = models.DateField(
        blank=True,
        null=True,
        help_text="Year the company was founded"
    )
    
    company_website = models.URLField(
        max_length=500,
        blank=True,
        help_text="Official company website address"
    )
    
    # Company Location (Composite address)
    company_location_street = models.CharField(
        max_length=255,
        blank=True,
        help_text="Street address"
    )
    
    company_location_city = models.CharField(
        max_length=100,
        blank=True,
        help_text="City"
    )
    
    company_location_country = models.CharField(
        max_length=100,
        blank=True,
        help_text="Country"
    )
    
    company_vision = models.TextField(
        blank=True,
        help_text="Long-term vision or statement of the company"
    )
    
    contact_email = models.EmailField(
        blank=True,
        help_text="Dedicated contact email for HR/recruitment"
    )
    
    contact_phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Dedicated contact phone number for the company"
    )
    
    # Metadata
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Automatically records the last time the profile was modified"
    )
    
    setup_completed = models.BooleanField(
        default=False,
        help_text="Indicates whether the user has completed the initial profile setup wizard"
    )
    
    class Meta:
        verbose_name = 'Employer Profile'
        verbose_name_plural = 'Employer Profiles'
        ordering = ['-updated_at']
    
    @property
    def company_address(self):
        parts = [
            self.company_location_street,
            self.company_location_city,
            self.company_location_country
        ]
        return ', '.join(part for part in parts if part)
    
    def __str__(self):
        return f"{self.company_name or 'Unnamed Company'} ({self.user.email})"
