from django.contrib import admin
from .models import ApplicantProfile, NotificationPreferences


@admin.register(ApplicantProfile)
class ApplicantProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'contact_number', 'education_level', 'experience', 'is_public', 'updated_at']
    list_filter = ['is_public', 'education_level', 'gender', 'updated_at']
    search_fields = ['user__email', 'first_name', 'last_name', 'contact_number']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'first_name', 'middle_name', 'last_name', 'title')
        }),
        ('Contact Information', {
            'fields': ('contact_number', 'profile_image')
        }),
        ('Professional Information', {
            'fields': ('resume', 'biography', 'education_level', 'experience')
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'gender', 'marital_status', 'nationality')
        }),
        ('Location', {
            'fields': ('location_street', 'location_city', 'location_country')
        }),
        ('Settings', {
            'fields': ('is_public', 'updated_at')
        }),
    )


@admin.register(NotificationPreferences)
class NotificationPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'notify_shortlisted', 'notify_applications', 'notify_job_alerts', 'updated_at']
    list_filter = ['notify_shortlisted', 'notify_applications', 'notify_job_alerts', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Notification Settings', {
            'fields': ('notify_shortlisted', 'notify_applications', 'notify_job_alerts')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
