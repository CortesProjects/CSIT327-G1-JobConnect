from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify
from datetime import date


class JobCategory(models.Model):
    """Job categories for classification."""
    code = models.CharField(max_length=50, unique=True, help_text="Unique code for programmatic reference")
    name = models.CharField(max_length=100, help_text="Display name for the category")
    description = models.TextField(blank=True, help_text="Optional description of the category")
    is_active = models.BooleanField(default=True, help_text="Whether this category is currently available")
    order = models.PositiveSmallIntegerField(default=0, help_text="Display order (lower numbers first)")
    
    class Meta:
        verbose_name = "Job Category"
        verbose_name_plural = "Job Categories"
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active', 'order']),
        ]
    
    def __str__(self):
        return self.name


class EmploymentType(models.Model):
    """Employment types (full-time, part-time, etc.)."""
    code = models.CharField(max_length=50, unique=True, help_text="Unique code for programmatic reference")
    name = models.CharField(max_length=100, help_text="Display name for the employment type")
    is_active = models.BooleanField(default=True, help_text="Whether this type is currently available")
    order = models.PositiveSmallIntegerField(default=0, help_text="Display order (lower numbers first)")
    
    class Meta:
        verbose_name = "Employment Type"
        verbose_name_plural = "Employment Types"
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active', 'order']),
        ]
    
    def __str__(self):
        return self.name


class EducationLevel(models.Model):
    """Education level requirements."""
    code = models.CharField(max_length=50, unique=True, help_text="Unique code for programmatic reference")
    name = models.CharField(max_length=100, help_text="Display name for the education level")
    is_active = models.BooleanField(default=True, help_text="Whether this level is currently available")
    order = models.PositiveSmallIntegerField(default=0, help_text="Display order (lower numbers first)")
    
    class Meta:
        verbose_name = "Education Level"
        verbose_name_plural = "Education Levels"
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active', 'order']),
        ]
    
    def __str__(self):
        return self.name


class ExperienceLevel(models.Model):
    """Experience level requirements."""
    code = models.CharField(max_length=50, unique=True, help_text="Unique code for programmatic reference")
    name = models.CharField(max_length=100, help_text="Display name for the experience level")
    min_years = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Minimum years of experience")
    max_years = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Maximum years of experience")
    is_active = models.BooleanField(default=True, help_text="Whether this level is currently available")
    order = models.PositiveSmallIntegerField(default=0, help_text="Display order (lower numbers first)")
    
    class Meta:
        verbose_name = "Experience Level"
        verbose_name_plural = "Experience Levels"
        ordering = ['order', 'min_years']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active', 'order']),
        ]
    
    def __str__(self):
        return self.name


class JobLevel(models.Model):
    """Job seniority levels (entry, mid, senior, etc.)."""
    code = models.CharField(max_length=50, unique=True, help_text="Unique code for programmatic reference")
    name = models.CharField(max_length=100, help_text="Display name for the job level")
    is_active = models.BooleanField(default=True, help_text="Whether this level is currently available")
    order = models.PositiveSmallIntegerField(default=0, help_text="Display order (lower numbers first)")
    
    class Meta:
        verbose_name = "Job Level"
        verbose_name_plural = "Job Levels"
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active', 'order']),
        ]
    
    def __str__(self):
        return self.name


class SalaryType(models.Model):
    """Salary payment frequency (hourly, monthly, yearly)."""
    code = models.CharField(max_length=50, unique=True, help_text="Unique code for programmatic reference")
    name = models.CharField(max_length=100, help_text="Display name for the salary type")
    is_active = models.BooleanField(default=True, help_text="Whether this type is currently available")
    order = models.PositiveSmallIntegerField(default=0, help_text="Display order (lower numbers first)")
    
    class Meta:
        verbose_name = "Salary Type"
        verbose_name_plural = "Salary Types"
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active', 'order']),
        ]
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tags for job postings."""
    name = models.CharField(max_length=50, unique=True, help_text="Tag name")
    slug = models.SlugField(max_length=50, unique=True, help_text="URL-friendly version")
    description = models.TextField(blank=True, help_text="Optional description")
    is_active = models.BooleanField(default=True, help_text="Whether this tag is currently available")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ============================================================================
# JOB MODEL
# ============================================================================

class Job(models.Model):
    
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
    
    # Foreign Key to JobCategory (job category)
    # Nullable during migration, will be required after data migration
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.PROTECT,
        related_name='jobs',
        null=True,
        blank=True,
        help_text="Job category"
    )
    location = models.CharField(max_length=100)
    
    # Salary information - Updated to NUMERIC(10, 2)
    min_salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Minimum salary amount"
    )
    max_salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Maximum salary amount"
    )
    # Nullable during migration
    salary_type = models.ForeignKey(
        SalaryType,
        on_delete=models.PROTECT,
        related_name='jobs',
        null=True,
        blank=True,
        help_text="Salary payment frequency"
    )
    
    # Advanced information - All Foreign Keys (nullable during migration)
    education = models.ForeignKey(
        EducationLevel,
        on_delete=models.PROTECT,
        related_name='jobs',
        null=True,
        blank=True,
        help_text="Required education level"
    )
    experience = models.ForeignKey(
        ExperienceLevel,
        on_delete=models.PROTECT,
        related_name='jobs',
        null=True,
        blank=True,
        help_text="Required experience level"
    )
    job_type = models.ForeignKey(
        EmploymentType,
        on_delete=models.PROTECT,
        related_name='jobs',
        null=True,
        blank=True,
        help_text="Type of employment"
    )
    vacancies = models.SmallIntegerField(
        default=1,
        help_text="Number of open positions"
    )
    expiration_date = models.DateField(help_text="Application deadline")
    job_level = models.ForeignKey(
        JobLevel,
        on_delete=models.PROTECT,
        related_name='jobs',
        null=True,
        blank=True,
        help_text="Seniority level of the position"
    )
    
    # Optional fields
    responsibilities = models.TextField(blank=True)
    
    # Legacy CharField field - keeping for backward compatibility during migration
    # Will be removed after data migration to category ForeignKey
    # Note: JOB_CATEGORIES constant removed, values stored in JobCategory table
    tags = models.CharField(max_length=255, blank=True, help_text="Legacy tags field, replaced by Many-to-Many Tag relationship")
    
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
    
    @property
    def tag_list(self):
        """Returns a list of tag names associated with this job."""
        return [job_tag.tag.name for job_tag in self.job_tags.select_related('tag')]
    
    def get_tag_names(self):
        """Returns comma-separated string of tag names."""
        return ', '.join(self.tag_list)


class JobTag(models.Model):
    """
    Junction table for Many-to-Many relationship between Jobs and Tags.
    Allows a job to have multiple tags and a tag to be associated with multiple jobs.
    """
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='job_tags',
        help_text="The job this tag is associated with"
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='job_tags',
        help_text="The tag associated with this job",
        null=True,
        blank=True
    )
    
    class Meta:
        unique_together = ['job', 'tag']
        ordering = ['tag__name']
        verbose_name = "Job Tag"
        verbose_name_plural = "Job Tags"
        indexes = [
            models.Index(fields=['job', 'tag']),
        ]
    
    def __str__(self):
        return f"{self.job.title} - {self.tag.name}"


class JobApplication(models.Model):
    """Links applicants to jobs and tracks application status."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('interview', 'Interview'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]
    
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_applications',
        limit_choices_to={'user_type': 'applicant'}
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    
    # Core fields
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Optional fields
    applicant_notes = models.TextField(
        blank=True,
        help_text="Cover letter or additional notes from the applicant"
    )
    employer_rating = models.IntegerField(
        null=True,
        blank=True,
        help_text="Rating given by employer (1-5)"
    )
    hired_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when status changed to 'hired'"
    )
    
    class Meta:
        unique_together = ['applicant', 'job']
        ordering = ['-application_date']
        indexes = [
            models.Index(fields=['applicant', 'status']),
            models.Index(fields=['job', 'status']),
            models.Index(fields=['-application_date']),
        ]
    
    def save(self, *args, **kwargs):
        # Auto-set hired_date when status changes to 'hired'
        if self.status == 'hired' and not self.hired_date:
            self.hired_date = date.today()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.applicant.email} - {self.job.title} ({self.status})"


class FavoriteJob(models.Model):
    """Tracks jobs that applicants have marked as favorites."""
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_jobs',
        limit_choices_to={'user_type': 'applicant'}
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['applicant', 'job']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['applicant', '-created_at']),
            models.Index(fields=['job']),
        ]
        verbose_name = "Favorite Job"
        verbose_name_plural = "Favorite Jobs"
    
    def __str__(self):
        return f"{self.applicant.email} - {self.job.title}"
