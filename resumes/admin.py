from django.contrib import admin
from .models import Resume

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'uploaded_at', 'is_default')
    list_filter = ('is_default', 'uploaded_at')
    search_fields = ('name', 'user__username', 'user__email')
    readonly_fields = ('uploaded_at',)
    list_per_page = 25
