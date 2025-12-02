from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify
from datetime import date
from utils.managers import JobManager


class JobCategory(models.Model):
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

class Job(models.Model):
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('closed', 'Closed'),
        ('draft', 'Draft'),
    ]


    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='jobs',
        limit_choices_to={'user_type': 'employer'}
    )

    company_name = models.CharField(max_length=255, default='', blank=True)

    title = models.CharField(max_length=100)
    description = models.TextField(help_text="Minimum 50 characters")
    
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.PROTECT,
        related_name='jobs',
        null=True,
        blank=True,
        help_text="Job category"
    )
    location = models.CharField(max_length=100)
    
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

    salary_type = models.ForeignKey(
        SalaryType,
        on_delete=models.PROTECT,
        related_name='jobs',
        null=True,
        blank=True,
        help_text="Salary payment frequency"
    )
    
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
    
    responsibilities = models.TextField(blank=True)
    tags = models.CharField(max_length=255, blank=True, help_text="Legacy tags field, replaced by Many-to-Many Tag relationship")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = JobManager()
    
    class Meta:
        ordering = ['-posted_at']
        indexes = [
            models.Index(fields=['-posted_at']),
            models.Index(fields=['employer', 'status']),
        ]

    def clean(self):
        errors = {}
        
        if not self.title or not self.title.strip():
            errors['title'] = 'Job title cannot be empty.'
        elif len(self.title) > 100:
            errors['title'] = 'Job title cannot exceed 100 characters.'
            
        if not self.description or not self.description.strip():
            errors['description'] = 'Job description cannot be empty.'
        elif len(self.description.strip()) < 50:
            errors['description'] = 'Description must be at least 50 characters.'
            
        if not self.location or not self.location.strip():
            errors['location'] = 'Location cannot be empty.'
            
        if self.min_salary and self.max_salary:
            if self.min_salary < 0:
                errors['min_salary'] = 'Minimum salary cannot be negative.'
            if self.max_salary < 0:
                errors['max_salary'] = 'Maximum salary cannot be negative.'
            if self.min_salary > self.max_salary:
                errors['min_salary'] = 'Minimum salary cannot be greater than maximum salary.'
                
        if self.expiration_date:
            if self.expiration_date < date.today():
                errors['expiration_date'] = 'Deadline must be a future date.'
                
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.expiration_date and self.expiration_date < date.today():
            self.status = 'expired'

        if not self.company_name or not str(self.company_name).strip():
            company = None
            try:
                company = getattr(self.employer, 'company_name', None) or getattr(self.employer, 'company', None)
            except Exception:
                company = None

            if not company:
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
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def get_tag_names(self):
        return ', '.join(self.tag_list)


class ApplicationStage(models.Model):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='application_stages',
        help_text="The job this stage belongs to"
    )
    name = models.CharField(
        max_length=100,
        help_text="Stage name (e.g., 'Shortlisted', 'Phone Interview', 'Hired')"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order of the stage (lower numbers first)"
    )
    is_system = models.BooleanField(
        default=False,
        help_text="True if this is a system-generated stage (e.g., 'Hired') that cannot be edited/deleted"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['job', 'order', 'created_at']
        unique_together = ['job', 'name']
        indexes = [
            models.Index(fields=['job', 'order']),
        ]
        verbose_name = "Application Stage"
        verbose_name_plural = "Application Stages"
    
    def __str__(self):
        return f"{self.job.title} - {self.name}"


class JobApplication(models.Model):
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
    
    stage = models.ForeignKey(
        'ApplicationStage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applications',
        help_text="Current stage in the hiring pipeline"
    )
    
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
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
        if self.status == 'hired' and not self.hired_date:
            self.hired_date = date.today()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.applicant.email} - {self.job.title} ({self.status})"


class FavoriteJob(models.Model):
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


class JobAlert(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_alerts',
        limit_choices_to={'user_type': 'applicant'}
    )
    alert_name = models.CharField(
        max_length=100,
        help_text="Name for this alert (e.g., 'Frontend Developer Jobs')"
    )
    job_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Job title keywords to match"
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        help_text="Preferred job location"
    )
    job_type = models.ForeignKey(
        EmploymentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_alerts',
        help_text="Preferred employment type"
    )
    job_category = models.ForeignKey(
        JobCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_alerts',
        help_text="Preferred job category"
    )
    min_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum desired salary"
    )
    max_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum desired salary"
    )
    keywords = models.CharField(
        max_length=500,
        blank=True,
        help_text="Additional keywords (comma-separated)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this alert is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = "Job Alert"
        verbose_name_plural = "Job Alerts"
    
    def __str__(self):
        return f"{self.user.email} - {self.alert_name}"
    
    def get_matching_jobs(self):
        """Returns queryset of active jobs matching this alert's criteria."""
        from django.db.models import Q
        
        jobs = Job.objects.filter(status='active', is_deleted=False)
        
        if self.job_title:
            jobs = jobs.filter(title__icontains=self.job_title)
        if self.location:
            jobs = jobs.filter(location__icontains=self.location)
        
        if self.job_type:
            jobs = jobs.filter(job_type=self.job_type)
        
        if self.job_category:
            jobs = jobs.filter(category=self.job_category)
        
        if self.min_salary:
            jobs = jobs.filter(
                Q(min_salary__gte=self.min_salary) | Q(min_salary__isnull=True)
            )
        
        if self.max_salary:
            jobs = jobs.filter(
                Q(max_salary__lte=self.max_salary) | Q(max_salary__isnull=True)
            )
        
        if self.keywords:
            keyword_list = [k.strip() for k in self.keywords.split(',') if k.strip()]
            keyword_query = Q()
            for keyword in keyword_list:
                keyword_query |= Q(title__icontains=keyword) | Q(description__icontains=keyword)
            jobs = jobs.filter(keyword_query)
        
        return jobs.distinct().order_by('-posted_date')
