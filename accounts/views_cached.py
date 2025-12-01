"""
Example of home view using caching utilities.
This version demonstrates how to use the caching utilities effectively.

To use this, replace the home function in accounts/views.py:
    from accounts.views_cached import home_cached as home
"""
from django.shortcuts import render, redirect
from utils.caching import get_site_statistics, get_popular_categories, get_featured_jobs


def get_user_dashboard_url(user):
    """Get dashboard URL based on user type."""
    if user.is_staff or user.user_type == 'ADMIN':
        return '/dashboard/admin/dashboards'
    return 'dashboard:dashboard'


def home_cached(request):
    """
    Home page view with caching for expensive queries.
    
    Benefits:
    - Reduces database load on home page
    - Faster page loads for unauthenticated users
    - Automatic cache invalidation after timeout
    """
    if request.user.is_authenticated:
        return redirect(get_user_dashboard_url(request.user))
    
    try:
        # Get cached statistics (5 min cache)
        stats = get_site_statistics()
        
        # Get cached popular categories (15 min cache)
        popular_categories = get_popular_categories(limit=8)
        
        # Get cached featured jobs (10 min cache)
        featured_jobs = get_featured_jobs(limit=3)
        
        context = {
            'live_jobs_count': stats['live_jobs_count'],
            'total_jobs_count': stats['total_jobs_count'],
            'companies_count': stats['companies_count'],
            'candidates_count': stats['candidates_count'],
            'popular_categories': popular_categories,
            'featured_jobs': featured_jobs,
        }
    except Exception:
        # Fallback to empty values
        context = {
            'live_jobs_count': 0,
            'total_jobs_count': 0,
            'companies_count': 0,
            'candidates_count': 0,
            'popular_categories': [],
            'featured_jobs': [],
        }
    
    return render(request, 'home.html', context)
