from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from .models import Job, FavoriteJob
from .forms import JobSearchForm
from django.db.models import Q
from notifications.utils import notify_application_received

def job_search(request):

    # GET parameters
    query = request.GET.get("query", "")
    location = request.GET.get("location", "")
    job_types = request.GET.getlist("job_type")     # Multiple checkboxes
    categories = request.GET.getlist("category")    # Multi-select (job categories)
    educations = request.GET.getlist("education")  # Multi-select
    experiences = request.GET.getlist("experience")
    job_levels = request.GET.getlist("job_level")
    salary_min = request.GET.get("salary_min")
    salary_max = request.GET.get("salary_max")

    # Start with all jobs
    jobs = Job.objects.all()

    # 🔍 Keyword search
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    # 📍 Location filter
    if location:
        jobs = jobs.filter(location__icontains=location)

    # 🧩 Job type (checkbox)
    if job_types:
        jobs = jobs.filter(job_type_id__in=job_types)

    # 🧩 Job category (replaces job_role)
    if categories:
        jobs = jobs.filter(category_id__in=categories)

    # 🧩 Education level
    if educations:
        jobs = jobs.filter(education_id__in=educations)

    # 🧩 Experience
    if experiences:
        jobs = jobs.filter(experience_id__in=experiences)

    # 🧩 Job level
    if job_levels:
        jobs = jobs.filter(job_level_id__in=job_levels)

    # 💰 Salary filter
    if salary_min:
        jobs = jobs.filter(salary_min__gte=salary_min)

    if salary_max:
        jobs = jobs.filter(salary_max__lte=salary_max)

    # DYNAMIC FILTER VALUES (from lookup tables)
    from .models import JobCategory, EmploymentType, EducationLevel, ExperienceLevel, JobLevel
    
    all_job_types = EmploymentType.objects.filter(is_active=True)
    all_categories = JobCategory.objects.filter(is_active=True)
    all_educations = EducationLevel.objects.filter(is_active=True)
    all_experiences = ExperienceLevel.objects.filter(is_active=True)
    all_job_levels = JobLevel.objects.filter(is_active=True)
    all_locations = Job.objects.values_list("location", flat=True).distinct()

    # Get favorited job IDs for logged-in applicants
    favorited_job_ids = []
    if request.user.is_authenticated and request.user.user_type == 'applicant':
        favorited_job_ids = list(
            FavoriteJob.objects.filter(applicant=request.user).values_list('job_id', flat=True)
        )

    context = {
        "jobs": jobs,
        "query": query,
        "location": location,
        "salary_min": salary_min,
        "salary_max": salary_max,

        # Dynamic filters
        "job_types": all_job_types,
        "categories": all_categories,  # Renamed from job_roles
        "educations": all_educations,
        "experiences": all_experiences,
        "job_levels": all_job_levels,
        "locations": all_locations,

        # Persist selected values
        "selected_job_types": job_types,
        "selected_categories": categories,  # Renamed from selected_job_roles
        "selected_educations": educations,
        "selected_experiences": experiences,
        "selected_job_levels": job_levels,
        
        # Favorite status
        "favorited_job_ids": favorited_job_ids,
    }

    return render(request, "jobs/job_search.html", context)

def job_suggestions(request):
    term = request.GET.get("term", "")
    if len(term) < 3:
        return JsonResponse([], safe=False)

    qs = Job.objects.filter(title__icontains=term)
    suggestions = list(qs.values_list("title", flat=True)[:8])
    return JsonResponse(suggestions, safe=False)


@login_required
@require_POST
def toggle_favorite_job(request, job_id):
    from dashboard.forms import FavoriteJobForm

    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Invalid request method. Use POST.'
        }, status=405)

    form = FavoriteJobForm(data={'job_id': job_id}, user=request.user)

    if not form.is_valid():
        errors = form.errors.get_json_data()
        error_message = 'Invalid request.'

        if '__all__' in errors:
            error_message = errors['__all__'][0]['message']
        elif 'job_id' in errors:
            error_message = errors['job_id'][0]['message']

        # If AJAX request, return JSON error
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', '')
        if is_ajax:
            return JsonResponse({
                'success': False,
                'error': error_message
            }, status=400)

        # Non-AJAX: set a message and redirect back
        from django.contrib import messages
        messages.error(request, error_message)
        from django.shortcuts import redirect
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # Get validated job from form
    job = form.cleaned_data['job']

    # Check if already favorited
    favorite = FavoriteJob.objects.filter(applicant=request.user, job=job).first()

    if favorite:
        # Remove from favorites
        favorite.delete()
        is_favorited = False
        message = 'Job removed from favorites'
    else:
        # Add to favorites
        FavoriteJob.objects.create(applicant=request.user, job=job)
        is_favorited = True
        message = 'Job added to favorites'

    # If AJAX, return JSON response
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', '')
    if is_ajax:
        return JsonResponse({
            'success': True,
            'is_favorited': is_favorited,
            'message': message
        })

    # Non-AJAX: show a message and redirect back
    from django.contrib import messages
    from django.shortcuts import redirect

    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def applicant_favorite_jobs(request):
    """Display applicant's favorite jobs."""
    if request.user.user_type != 'applicant':
        return JsonResponse({
            'success': False,
            'error': 'Only applicants can view favorite jobs'
        }, status=403)
    
    # Get all favorite jobs for the current applicant
    favorites = FavoriteJob.objects.filter(
        applicant=request.user
    ).select_related('job', 'job__employer', 'job__category')
    
    context = {
        'favorites': favorites,
        'favorite_count': favorites.count()
    }
    
    return render(request, 'jobs/favorite_jobs.html', context)


def job_detail(request, job_id):
    """Display detailed information about a specific job."""
    # Fetch job with all related data
    job = get_object_or_404(
        Job.objects.select_related(
            'employer',
            'category',
            'job_type',
            'education',
            'experience',
            'job_level',
            'salary_type'
        ),
        id=job_id
    )
    
    # Determine breadcrumb source from referer or query param
    source = request.GET.get('from', '')
    referer = request.META.get('HTTP_REFERER', '')
    
    breadcrumb_source = 'search'  # default
    breadcrumb_label = 'Search Jobs'
    breadcrumb_url = 'dashboard:applicant_search_jobs'
    
    if source:
        breadcrumb_source = source
    elif 'applied' in referer or 'applications' in referer:
        breadcrumb_source = 'applied'
    elif 'favorite' in referer:
        breadcrumb_source = 'favorites'
    elif 'my-jobs' in referer or 'myjobs' in referer:
        breadcrumb_source = 'myjobs'
    elif 'recent' in referer:
        breadcrumb_source = 'recent'
    
    # Map source to breadcrumb label and URL
    breadcrumb_map = {
        'applied': ('My Applications', 'dashboard:applicant_applied_jobs'),
        'favorites': ('Favorite Jobs', 'dashboard:applicant_favorite_jobs'),
        'search': ('Search Jobs', 'dashboard:applicant_search_jobs'),
        'alert': ('Job Alerts', 'dashboard:applicant_dashboard'),
        'myjobs': ('My Jobs', 'dashboard:employer_my_jobs'),
        'recent': ('Recently Posted', 'dashboard:employer_dashboard'),
    }
    
    if breadcrumb_source in breadcrumb_map:
        breadcrumb_label, breadcrumb_url = breadcrumb_map[breadcrumb_source]
    
    # Check if user has favorited this job
    is_favorited = False
    has_applied = False
    resumes = []
    
    if request.user.is_authenticated and request.user.user_type == 'applicant':
        is_favorited = FavoriteJob.objects.filter(
            applicant=request.user,
            job=job
        ).exists()
        
        # Check if user has already applied
        from .models import JobApplication
        has_applied = JobApplication.objects.filter(
            applicant=request.user,
            job=job
        ).exists()
        
        # Get applicant's resumes for the apply modal
        # Currently using the single resume field from ApplicantProfile
        if hasattr(request.user, 'applicant_profile_rel'):
            profile = request.user.applicant_profile_rel
            if profile.resume:
                # Create a simple object to pass to template
                resumes = [{
                    'id': 1,  # Dummy ID since we only have one resume field
                    'name': profile.resume.name.split('/')[-1] if profile.resume.name else 'My Resume'
                }]
    
    # Determine which base template to use
    if request.user.is_authenticated and request.user.user_type == 'employer':
        base_template = 'dashboard/employer/employer_dashboard_base.html'
    else:
        base_template = 'dashboard/applicant/applicant_dashboard_base.html'
    
    # Calculate days since job was posted (for edit window check)
    from django.utils import timezone
    days_since_posted = (timezone.now() - job.posted_at).days
    can_edit = days_since_posted <= 7
    
    # If `goto=applications` present and the current user is the job owner,
    # perform a server-side redirect directly to the employer applications
    # page. This causes an immediate HTTP redirect instead of relying on
    # client-side JS. Note: server redirect does NOT leave the job detail
    # URL in browser history (back will return to the previous page).
    goto = request.GET.get('goto', '')
    if goto == 'applications' and request.user.is_authenticated and getattr(request.user, 'user_type', '') == 'employer' and job.employer == request.user:
        from django.shortcuts import redirect
        return redirect('dashboard:employer_job_applications', job.id)

    context = {
        'job': job,
        'is_favorited': is_favorited,
        'has_applied': has_applied,
        'resumes': resumes,
        'breadcrumb_label': breadcrumb_label,
        'breadcrumb_url': breadcrumb_url,
        'base_template': base_template,
        'days_since_posted': days_since_posted,
        'can_edit_job': can_edit,
    }
    # If the query param `goto=applications` was provided, and the current user
    # is the job owner (employer), set a context flag so the template can
    # perform a client-side redirect to the applications view while keeping
    # the job detail in the browser history.
    goto = request.GET.get('goto', '')
    context['goto_applications'] = (goto == 'applications' and request.user.is_authenticated and getattr(request.user, 'user_type', '') == 'employer')
    
    return render(request, 'jobs/job_detail.html', context)


@login_required
@require_POST
def apply_job(request, job_id):
    """Handle job application submission with Django validation."""
    from .forms import JobApplicationForm
    from .models import JobApplication
    from django.contrib import messages
    
    # Create form with POST data and current user
    form_data = request.POST.copy()
    form_data['job_id'] = job_id
    form = JobApplicationForm(data=form_data, user=request.user)
    
    if not form.is_valid():
        # Get first error message
        error_message = 'Invalid application.'
        errors = form.errors
        
        if '__all__' in errors:
            error_message = errors['__all__'][0]
        elif 'job_id' in errors:
            error_message = errors['job_id'][0]
        elif 'resume_id' in errors:
            error_message = errors['resume_id'][0]
        elif 'cover_letter' in errors:
            error_message = errors['cover_letter'][0]
        else:
            # Get first field error
            for field, field_errors in errors.items():
                if field_errors:
                    error_message = field_errors[0]
                    break
        
        # If AJAX request, return JSON error; otherwise set message and redirect back
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', '')
        if is_ajax:
            return JsonResponse({
                'success': False,
                'error': error_message
            }, status=400)

        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, error_message)
        return redirect(request.META.get('HTTP_REFERER', reverse('jobs:job_detail', kwargs={'job_id': job_id})))
    
    # Get validated data
    job = form.cleaned_data['job']
    cover_letter = form.cleaned_data.get('cover_letter', '')
    
    try:
        # Create job application
        application = JobApplication.objects.create(
            applicant=request.user,
            job=job,
            applicant_notes=cover_letter,
            status='pending'
        )
        
        # Notify employer about new application
        notify_application_received(job.employer, request.user, job, application)
        
        # If the request was AJAX, return JSON response; otherwise redirect back with message
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', '')
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': f'Successfully applied for {job.title}!',
                'application_id': application.id
            })

        from django.contrib import messages
        from django.shortcuts import redirect
        messages.success(request, f'Successfully applied for {job.title}!')
        return redirect(request.META.get('HTTP_REFERER', reverse('jobs:job_detail', kwargs={'job_id': job_id})))
    
    except Exception as e:
        # On errors, return JSON for AJAX or set message + redirect for normal requests
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', '')
        error_msg = f'Failed to submit application: {str(e)}'
        if is_ajax:
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=500)

        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, error_msg)
        return redirect(request.META.get('HTTP_REFERER', reverse('jobs:job_detail', kwargs={'job_id': job_id})))


@login_required
@require_POST
def delete_job(request, job_id):
    """Delete a job posting (employer only)."""
    from django.contrib import messages
    from django.shortcuts import redirect
    
    # Get job
    job = get_object_or_404(Job, id=job_id)
    
    # Verify user is employer and owns this job
    if request.user.user_type != 'employer':
        return JsonResponse({
            'success': False,
            'error': 'Only employers can delete jobs.'
        }, status=403)
    
    if job.employer != request.user:
        return JsonResponse({
            'success': False,
            'error': 'You do not have permission to delete this job.'
        }, status=403)
    
    try:
        job_title = job.title
        job.delete()
        
        messages.success(request, f'Job "{job_title}" has been deleted successfully.')
        
        # Return JSON for AJAX requests
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Job "{job_title}" deleted successfully.',
                'redirect_url': reverse('dashboard:employer_my_jobs')
            })
        
        return redirect('dashboard:employer_my_jobs')
    
    except Exception as e:
        error_msg = f'Failed to delete job: {str(e)}'
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=500)
        
        messages.error(request, error_msg)
        return redirect('jobs:job_detail', job_id=job_id)


@login_required
@require_POST
def mark_job_expired(request, job_id):
    """Mark a job as expired (employer only)."""
    from django.contrib import messages
    from django.shortcuts import redirect
    
    # Get job
    job = get_object_or_404(Job, id=job_id)
    
    # Verify user is employer and owns this job
    if request.user.user_type != 'employer':
        return JsonResponse({
            'success': False,
            'error': 'Only employers can mark jobs as expired.'
        }, status=403)
    
    if job.employer != request.user:
        return JsonResponse({
            'success': False,
            'error': 'You do not have permission to modify this job.'
        }, status=403)
    
    # Check if already expired
    if job.status == 'expired':
        return JsonResponse({
            'success': False,
            'error': 'This job is already marked as expired.'
        }, status=400)
    
    try:
        # Set status and update the expiration_date to now so model logic and listings reflect when it was expired
        from django.utils import timezone
        job.status = 'expired'
        try:
            # expiration_date is a DateField; set to today's date in current timezone
            job.expiration_date = timezone.localdate()
        except Exception:
            # fallback to date.today
            from datetime import date as _date
            job.expiration_date = _date.today()
        job.save()
        
        messages.success(request, f'Job "{job.title}" has been marked as expired.')
        
        # Return JSON for AJAX requests
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Job "{job.title}" marked as expired.',
                'redirect_url': reverse('jobs:job_detail', kwargs={'job_id': job_id})
            })
        
        return redirect('jobs:job_detail', job_id=job_id)
    
    except Exception as e:
        error_msg = f'Failed to mark job as expired: {str(e)}'
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=500)
        
        messages.error(request, error_msg)
        return redirect('jobs:job_detail', job_id=job_id)