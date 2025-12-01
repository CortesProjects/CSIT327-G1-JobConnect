"""
Class-Based Views (CBV) examples showing Django best practices.
These demonstrate how to convert function-based views to CBVs.

To use these views, update the corresponding urls.py:
    path('my-jobs/', EmployerJobListView.as_view(), name='employer_my_jobs'),
"""
from django.views.generic import ListView, DetailView
from django.db.models import Count, Q
from utils.mixins import EmployerRequiredMixin, ApplicantRequiredMixin
from jobs.models import Job, FavoriteJob
from dashboard.forms import JobSearchForm


class EmployerJobListView(EmployerRequiredMixin, ListView):
    """
    Display all jobs posted by the employer with filtering.
    Replaces: dashboard.views.employer_my_jobs
    """
    model = Job
    template_name = 'dashboard/employer/employer_my_jobs.html'
    context_object_name = 'all_jobs'
    
    def get_queryset(self):
        """Filter jobs by current employer and annotate with application counts."""
        queryset = Job.objects.filter(
            employer=self.request.user
        ).annotate(
            applications_count=Count('applications')
        ).order_by('-posted_at')
        
        # Apply status filter from GET parameters
        status_filter = self.request.GET.get('status', 'all')
        if status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add additional context for template."""
        context = super().get_context_data(**kwargs)
        context['has_jobs'] = self.get_queryset().exists()
        context['total_jobs'] = self.get_queryset().count()
        context['status_filter'] = self.request.GET.get('status', 'all')
        return context


class ApplicantJobSearchView(ApplicantRequiredMixin, ListView):
    """
    Search jobs for applicants with comprehensive filters.
    Replaces: dashboard.views.applicant_search_jobs
    """
    model = Job
    template_name = 'dashboard/applicant/applicant_search_jobs.html'
    context_object_name = 'jobs'
    paginate_by = 20  # Automatic pagination
    
    def get_queryset(self):
        """Apply search filters from form validation."""
        from jobs.models import JobCategory, EducationLevel, ExperienceLevel, JobLevel
        
        # Get filter options for form
        category_choices = [('', 'Category')] + [
            (str(c.id), c.name) for c in JobCategory.objects.filter(is_active=True)
        ]
        education_choices = [('', 'Education')] + [
            (str(e.id), e.name) for e in EducationLevel.objects.filter(is_active=True)
        ]
        experience_choices = [('', 'Experience')] + [
            (str(e.id), e.name) for e in ExperienceLevel.objects.filter(is_active=True)
        ]
        job_level_choices = [('', 'Level')] + [
            (str(j.id), j.name) for j in JobLevel.objects.filter(is_active=True)
        ]
        
        # Initialize form with GET data
        form = JobSearchForm(
            self.request.GET or None,
            category_choices=category_choices,
            education_choices=education_choices,
            experience_choices=experience_choices,
            job_level_choices=job_level_choices
        )
        
        # Start with active jobs
        queryset = Job.objects.filter(status='active').annotate(
            applications_count=Count('applications')
        )
        
        # Apply filters if form is valid
        if form.is_valid():
            cleaned_data = form.cleaned_data
            
            # Keyword search
            query = cleaned_data.get('query')
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(company_name__icontains=query) |
                    Q(tags__icontains=query)
                ).distinct()
            
            # Category filter
            category_val = cleaned_data.get('category')
            if category_val:
                queryset = queryset.filter(category_id=category_val)
            
            # Education filter
            education_val = cleaned_data.get('education')
            if education_val:
                queryset = queryset.filter(education_id=education_val)
            
            # Experience filter
            experience_val = cleaned_data.get('experience')
            if experience_val:
                queryset = queryset.filter(experience_id=experience_val)
            
            # Job level filter
            job_level_val = cleaned_data.get('job_level')
            if job_level_val:
                queryset = queryset.filter(job_level_id=job_level_val)
            
            # Salary filters
            salary_min = cleaned_data.get('salary_min')
            if salary_min:
                queryset = queryset.filter(min_salary__gte=salary_min)
            
            salary_max = cleaned_data.get('salary_max')
            if salary_max:
                queryset = queryset.filter(max_salary__lte=salary_max)
        
        return queryset.order_by('-posted_at')
    
    def get_context_data(self, **kwargs):
        """Add form and filter options to context."""
        from jobs.models import JobCategory, EducationLevel, ExperienceLevel, JobLevel
        
        context = super().get_context_data(**kwargs)
        
        # Get filter options
        all_categories = JobCategory.objects.filter(is_active=True)
        all_educations = EducationLevel.objects.filter(is_active=True)
        all_experiences = ExperienceLevel.objects.filter(is_active=True)
        all_job_levels = JobLevel.objects.filter(is_active=True)
        
        # Prepare choices for form
        category_choices = [('', 'Category')] + [(str(c.id), c.name) for c in all_categories]
        education_choices = [('', 'Education')] + [(str(e.id), e.name) for e in all_educations]
        experience_choices = [('', 'Experience')] + [(str(e.id), e.name) for e in all_experiences]
        job_level_choices = [('', 'Level')] + [(str(j.id), j.name) for j in all_job_levels]
        
        # Add form
        context['form'] = JobSearchForm(
            self.request.GET or None,
            category_choices=category_choices,
            education_choices=education_choices,
            experience_choices=experience_choices,
            job_level_choices=job_level_choices
        )
        
        context['categories'] = all_categories
        context['educations'] = all_educations
        context['experiences'] = all_experiences
        context['job_levels'] = all_job_levels
        
        # Get favorited job IDs
        context['favorited_job_ids'] = list(
            FavoriteJob.objects.filter(applicant=self.request.user).values_list('job_id', flat=True)
        )
        
        return context


class ApplicantFavoriteJobsView(ApplicantRequiredMixin, ListView):
    """
    Display applicant's favorite jobs.
    Replaces: dashboard.views.applicant_favorite_jobs
    """
    model = FavoriteJob
    template_name = 'dashboard/applicant/applicant_favorite_jobs.html'
    context_object_name = 'favorites'
    
    def get_queryset(self):
        """Get all favorite jobs with related data."""
        return FavoriteJob.objects.filter(
            applicant=self.request.user
        ).select_related(
            'job',
            'job__employer',
            'job__category',
            'job__job_type',
            'job__education',
            'job__experience',
            'job__job_level'
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """Add favorite count and job IDs."""
        context = super().get_context_data(**kwargs)
        context['favorite_count'] = self.get_queryset().count()
        context['favorited_job_ids'] = list(self.get_queryset().values_list('job_id', flat=True))
        return context
