"""
Caching utilities for JobConnect.
Demonstrates Django's caching framework best practices.
"""
from django.core.cache import cache
from django.db.models import Count
from functools import wraps
import hashlib
import json


def make_cache_key(prefix, *args, **kwargs):
    
    key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
    key_hash = hashlib.md5(key_data.encode()).hexdigest()
    return f"{prefix}:{key_hash}"


def cache_result(timeout=300, key_prefix='default'):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = make_cache_key(key_prefix, *args, **kwargs)
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Cache miss - compute result
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


@cache_result(timeout=900, key_prefix='popular_categories')
def get_popular_categories(limit=8):
    """
    Get popular job categories with job counts (only active jobs).
    Cached for 15 minutes.
    """
    from jobs.models import JobCategory
    from django.db.models import Q
    
    return list(
        JobCategory.objects.annotate(
            job_count=Count('jobs', filter=Q(jobs__status='active'))
        ).filter(
            job_count__gt=0,
            is_active=True
        ).order_by('-job_count')[:limit]
    )


@cache_result(timeout=600, key_prefix='featured_jobs')
def get_featured_jobs(limit=3):
    """
    Get featured/recent active jobs.
    Cached for 10 minutes.
    """
    from jobs.models import Job
    
    return list(
        Job.objects.filter(
            status='active'
        ).annotate(
            applications_count=Count('applications')
        ).order_by('-posted_at')[:limit]
    )


@cache_result(timeout=300, key_prefix='site_stats')
def get_site_statistics():
    """
    Get site-wide statistics (active job counts, user counts).
    Both live_jobs_count and total_jobs_count show only active jobs.
    Cached for 5 minutes.
    """
    from jobs.models import Job
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    active_jobs = Job.objects.filter(status='active')
    
    return {
        'live_jobs_count': active_jobs.count(),
        'total_jobs_count': active_jobs.count(),  # Show only active jobs
        'companies_count': User.objects.filter(user_type='employer').count(),
        'candidates_count': User.objects.filter(user_type='applicant').count(),
    }


def invalidate_job_caches(job_id=None):
    """
    Invalidate job-related caches when jobs are created/updated/deleted.
    Call this in save() or delete() methods, or in signals.
    """
    patterns = [
        'featured_jobs:*',
        'site_stats:*',
        'popular_categories:*',
    ]
    
    if job_id:
        patterns.append(f'job_detail:{job_id}:*')
    
    # Django's cache doesn't support pattern-based deletion by default
    # This is a simple approach - for production, consider Redis with pattern matching
    for pattern in patterns:
        cache.delete(pattern)


def get_or_set_cache(key, callable_func, timeout=300):
    """
    Generic cache get-or-set pattern.
    
    Usage:
        stats = get_or_set_cache(
            'user_stats_123',
            lambda: expensive_query(user_id=123),
            timeout=600
        )
    """
    result = cache.get(key)
    if result is None:
        result = callable_func()
        cache.set(key, result, timeout)
    return result


# Example of per-user caching
def get_user_notification_count(user_id):
    """
    Get unread notification count for a user with caching.
    Cached per user for 1 minute.
    """
    cache_key = f'notification_count:user:{user_id}'
    
    count = cache.get(cache_key)
    if count is None:
        from notifications.models import Notification
        count = Notification.objects.filter(user_id=user_id, is_read=False).count()
        cache.set(cache_key, count, 60)  # Cache for 1 minute
    
    return count


def invalidate_user_notification_cache(user_id):
    """Invalidate notification cache when notifications change."""
    cache_key = f'notification_count:user:{user_id}'
    cache.delete(cache_key)
