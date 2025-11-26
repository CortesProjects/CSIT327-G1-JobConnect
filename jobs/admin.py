from django.contrib import admin
from .models import Job, JobTag, JobApplication
from .lookup_models import (
    JobCategory, EmploymentType, EducationLevel,
    ExperienceLevel, JobLevel, SalaryType, Tag
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


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


class JobTagInline(admin.TabularInline):
    model = JobTag
    extra = 1
    autocomplete_fields = ['tag']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company_name', 'category', 'job_type', 'location', 'status', 'posted_at']
    list_filter = ['status', 'category', 'job_type', 'job_level', 'posted_at']
    search_fields = ['title', 'company_name', 'description', 'location']
    readonly_fields = ['posted_at', 'updated_at']
    autocomplete_fields = ['employer', 'category', 'job_type', 'education', 'experience', 'job_level', 'salary_type']
    inlines = [JobTagInline]
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


@admin.register(JobTag)
class JobTagAdmin(admin.ModelAdmin):
    list_display = ['job', 'tag', 'created_at']
    list_filter = ['created_at']
    search_fields = ['job__title', 'tag__name']
    autocomplete_fields = ['job', 'tag']


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'job', 'status', 'application_date']
    list_filter = ['status', 'application_date']
    search_fields = ['applicant__email', 'job__title']
    readonly_fields = ['application_date']
