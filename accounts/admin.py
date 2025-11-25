from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserVerification, UserSocialLink


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'user_type', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['user_type', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('User Type', {'fields': ('user_type', 'middle_name')}),
    )


@admin.register(UserVerification)
class UserVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'verification_date', 'admin_verifier']
    list_filter = ['status', 'verification_date']
    search_fields = ['user__email', 'user__username', 'notes']
    readonly_fields = ['verification_date']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Verification Details', {
            'fields': ('status', 'admin_verifier', 'verification_date', 'notes')
        }),
    )


@admin.register(UserSocialLink)
class UserSocialLinkAdmin(admin.ModelAdmin):
    """Admin interface for UserSocialLink"""
    list_display = ['user', 'platform', 'url', 'created_at']
    list_filter = ['platform', 'created_at']
    search_fields = ['user__email', 'user__username', 'url']
    ordering = ['-created_at']
