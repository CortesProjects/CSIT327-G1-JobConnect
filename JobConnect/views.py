"""
Custom error handler views for JobConnect.
These provide user-friendly error pages that match the application design.
"""
from django.shortcuts import render


def custom_404(request, exception=None):
    """Handle 404 - Page Not Found errors."""
    return render(request, '404.html', status=404)


def custom_403(request, exception=None):
    """Handle 403 - Permission Denied errors."""
    return render(request, '403.html', status=403)


def custom_500(request):
    """Handle 500 - Internal Server Error."""
    return render(request, '500.html', status=500)
