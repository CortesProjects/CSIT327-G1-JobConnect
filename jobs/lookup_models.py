"""
Normalized lookup tables for Job model.
These tables store controlled vocabulary for job attributes.
"""
from django.db import models


class JobCategory(models.Model):
    """Job categories (previously called job_role)."""
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
    """
    Global tags that can be associated with jobs.
    Implements Many-to-Many through JobTag junction table.
    """
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
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
