from django.contrib import admin
from .models import (
    Job, JobApplication, FavoriteJob,
    JobCategory, EmploymentType, EducationLevel,
    ExperienceLevel, JobLevel, SalaryType
)


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['code', 'name', 'description']
    ordering = ['order', 'name']


@admin.register(EmploymentType)
class EmploymentTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['order', 'name']


@admin.register(EducationLevel)
class EducationLevelAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['order', 'name']


@admin.register(ExperienceLevel)
class ExperienceLevelAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'min_years', 'max_years', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['order', 'min_years']


@admin.register(JobLevel)
class JobLevelAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['order', 'name']


@admin.register(SalaryType)
class SalaryTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['order', 'name']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company_name', 'category', 'job_type', 'location', 'status', 'posted_at']
    list_filter = ['status', 'category', 'job_type', 'job_level', 'posted_at']
    search_fields = ['title', 'company_name', 'description', 'location', 'tags']
    readonly_fields = ['posted_at', 'updated_at']
    autocomplete_fields = ['employer', 'category', 'job_type', 'education', 'experience', 'job_level', 'salary_type']
    fieldsets = (
        ('Basic Information', {
            'fields': ('employer', 'company_name', 'title', 'description', 'category', 'location')
        }),
        ('Job Details', {
            'fields': ('job_type', 'job_level', 'education', 'experience', 'vacancies', 'expiration_date')
        }),
        ('Salary Information', {
            'fields': ('min_salary', 'max_salary', 'salary_type')
        }),
        ('Additional Information', {
            'fields': ('responsibilities', 'status')
        }),
        ('Metadata', {
            'fields': ('posted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'job', 'status', 'application_date']
    list_filter = ['status', 'application_date']
    search_fields = ['applicant__email', 'job__title']
    readonly_fields = ['application_date']


@admin.register(FavoriteJob)
class FavoriteJobAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'job', 'created_at']
    list_filter = ['created_at']
    search_fields = ['applicant__email', 'applicant__first_name', 'applicant__last_name', 'job__title']
    readonly_fields = ['created_at']
    autocomplete_fields = ['applicant', 'job']
    date_hierarchy = 'created_at'
