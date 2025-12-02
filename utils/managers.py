"""
Custom Django managers and querysets for reusable query logic.
Managers provide a clean interface for common database operations.
"""
from django.db import models
from django.utils import timezone


class ActiveJobManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='active')


class JobQuerySet(models.QuerySet):
    
    def active(self):
        return self.filter(status='active')
    
    def expired(self):
        return self.filter(status='expired')
    
    def by_employer(self, employer):
        return self.filter(employer=employer)
    
    def with_application_counts(self):
        return self.annotate(applications_count=models.Count('applications'))
    
    def recent(self, days=7):
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        return self.filter(posted_at__gte=cutoff_date)
    
    def search(self, query):
        if not query:
            return self
        return self.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(company_name__icontains=query) |
            models.Q(tags__icontains=query)
        ).distinct()
    
    def filter_by_salary_range(self, min_salary=None, max_salary=None):
        qs = self
        if min_salary:
            qs = qs.filter(min_salary__gte=min_salary)
        if max_salary:
            qs = qs.filter(max_salary__lte=max_salary)
        return qs


class JobManager(models.Manager):
    def get_queryset(self):
        return JobQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def with_application_counts(self):
        return self.get_queryset().with_application_counts()
    
    def recent(self, days=7):
        return self.get_queryset().recent(days)
    
    def search(self, query):
        return self.get_queryset().search(query)


class NotificationQuerySet(models.QuerySet):
    
    def unread(self):
        return self.filter(is_read=False)
    
    def read(self):
        return self.filter(is_read=True)
    
    def by_type(self, notification_type):
        return self.filter(notification_type=notification_type)
    
    def mark_all_read(self):
        return self.update(is_read=True, read_at=timezone.now())
    
    def recent(self, limit=20):
        return self.order_by('-created_at')[:limit]


class NotificationManager(models.Manager):
    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)
    
    def unread(self):
        return self.get_queryset().unread()
    
    def recent(self, limit=20):
        return self.get_queryset().recent(limit)
