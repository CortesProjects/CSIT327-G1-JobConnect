from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from utils.mixins import applicant_required, employer_required
from .models import Job, FavoriteJob
from .forms import JobSearchForm
from django.db.models import Q, Value, DecimalField
from notifications.utils import notify_application_received
from django.db.models.functions import Coalesce

def job_search(request):
    from decimal import Decimal, InvalidOperation
    from .models import JobCategory, EmploymentType, EducationLevel, ExperienceLevel, JobLevel

    query = request.GET.get("query", "").strip()
    location = request.GET.get("location", "").strip()

    job_types = [v for v in request.GET.getlist("job_type") if v != ""]
    categories = [v for v in request.GET.getlist("category") if v != ""]
    educations = [v for v in request.GET.getlist("education") if v != ""]
    experiences = [v for v in request.GET.getlist("experience") if v != ""]
    job_levels = [v for v in request.GET.getlist("job_level") if v != ""]

    salary_min_raw = request.GET.get("salary_min", "").strip()
    salary_max_raw = request.GET.get("salary_max", "").strip()

    sort = request.GET.get("sort", "recent")

    from django.utils import timezone
    today = timezone.localdate()

    jobs = Job.objects.select_related(
        'employer',
        'category',
        'job_type',
        'education',
        'experience',
        'job_level',
        'salary_type'
    ).filter(
        status='active',
        expiration_date__gte=today,
    )

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    if location:
        jobs = jobs.filter(location__icontains=location)

    if job_types:
        jobs = jobs.filter(job_type_id__in=job_types)

    if categories:
        jobs = jobs.filter(category_id__in=categories)

    if educations:
        jobs = jobs.filter(education_id__in=educations)

    if experiences:
        jobs = jobs.filter(experience_id__in=experiences)

    if job_levels:
        jobs = jobs.filter(job_level_id__in=job_levels)

    if salary_min_raw:
        try:
            salary_min_val = Decimal(salary_min_raw)
            jobs = jobs.filter(min_salary__gte=salary_min_val)
        except (InvalidOperation, ValueError):
            pass

    if salary_max_raw:
        try:
            salary_max_val = Decimal(salary_max_raw)
            jobs = jobs.filter(max_salary__lte=salary_max_val)
        except (InvalidOperation, ValueError):
            pass

    all_job_types = EmploymentType.objects.filter(is_active=True)
    all_categories = JobCategory.objects.filter(is_active=True)
    all_educations = EducationLevel.objects.filter(is_active=True)
    all_experiences = ExperienceLevel.objects.filter(is_active=True)
    all_job_levels = JobLevel.objects.filter(is_active=True)
    all_locations = Job.objects.values_list("location", flat=True).distinct()

    favorited_job_ids = []
    if request.user.is_authenticated and getattr(request.user, "user_type", "") == 'applicant':
        favorited_job_ids = list(
            FavoriteJob.objects.filter(applicant=request.user).values_list('job_id', flat=True)
        )

    if sort == "salary_low":
        jobs = jobs.annotate(
            sort_salary=Coalesce('min_salary', 'max_salary', Value(0, output_field=DecimalField()))
        ).order_by('sort_salary', '-posted_at')
    elif sort == "salary_high":
        jobs = jobs.annotate(
            sort_salary=Coalesce('max_salary', 'min_salary', Value(0, output_field=DecimalField()))
        ).order_by('-sort_salary', '-posted_at')
    else:
        jobs = jobs.order_by('-posted_at')


    context = {
        "jobs": jobs,
        "query": query,
        "location": location,
        "salary_min": salary_min_raw,
        "salary_max": salary_max_raw,

        "job_types": all_job_types,
        "categories": all_categories,
        "educations": all_educations,
        "experiences": all_experiences,
        "job_levels": all_job_levels,
        "locations": all_locations,
        "sort": sort,

        "selected_job_types": job_types,
        "selected_categories": categories,
        "selected_educations": educations,
        "selected_experiences": experiences,
        "selected_job_levels": job_levels,

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


@applicant_required
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

        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', '')
        if is_ajax:
            return JsonResponse({
                'success': False,
                'error': error_message
            }, status=400)

        from django.contrib import messages
        messages.error(request, error_message)
        from django.shortcuts import redirect
        return redirect(request.META.get('HTTP_REFERER', '/'))

    job = form.cleaned_data['job']

    favorite = FavoriteJob.objects.filter(applicant=request.user, job=job).first()

    if favorite:
        favorite.delete()
        is_favorited = False
        message = 'Job removed from favorites'
    else:
        FavoriteJob.objects.create(applicant=request.user, job=job)
        is_favorited = True
        message = 'Job added to favorites'

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', '')
    if is_ajax:
        return JsonResponse({
            'success': True,
            'is_favorited': is_favorited,
            'message': message
        })

    from django.contrib import messages
    from django.shortcuts import redirect

    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', '/'))



def job_detail(request, job_id):
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
    
    source = request.GET.get('from', '')
    referer = request.META.get('HTTP_REFERER', '')
    
    breadcrumb_source = 'search'  
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
    
    is_favorited = False
    has_applied = False
    resumes = []
    
    if request.user.is_authenticated and request.user.user_type == 'applicant':
        is_favorited = FavoriteJob.objects.filter(
            applicant=request.user,
            job=job
        ).exists()
        
        from .models import JobApplication
        has_applied = JobApplication.objects.filter(
            applicant=request.user,
            job=job
        ).exists()
        
        if hasattr(request.user, 'applicant_profile_rel'):
            profile = request.user.applicant_profile_rel
            if profile.resume:
                resumes = [{
                    'id': 1,  
                    'name': profile.resume.name.split('/')[-1] if profile.resume.name else 'My Resume'
                }]
    
    if request.user.is_authenticated and request.user.user_type == 'employer':
        base_template = 'dashboard/employer/employer_dashboard_base.html'
    else:
        base_template = 'dashboard/applicant/applicant_dashboard_base.html'
    
    from django.utils import timezone
    days_since_posted = (timezone.now() - job.posted_at).days
    can_edit = days_since_posted <= 7
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
    goto = request.GET.get('goto', '')
    context['goto_applications'] = (goto == 'applications' and request.user.is_authenticated and getattr(request.user, 'user_type', '') == 'employer')
    
    return render(request, 'jobs/job_detail.html', context)


@applicant_required
@require_POST
def apply_job(request, job_id):
    from .forms import JobApplicationForm
    from .models import JobApplication
    from django.contrib import messages
    
    form_data = request.POST.copy()
    form_data['job_id'] = job_id
    form = JobApplicationForm(data=form_data, user=request.user)
    
    if not form.is_valid():
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
            for field, field_errors in errors.items():
                if field_errors:
                    error_message = field_errors[0]
                    break
        
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
    
    job = form.cleaned_data['job']
    cover_letter = form.cleaned_data.get('cover_letter', '')
    
    try:
        application = JobApplication.objects.create(
            applicant=request.user,
            job=job,
            applicant_notes=cover_letter,
            status='pending'
        )
        
        notify_application_received(job.employer, request.user, job, application)
        
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


@employer_required
@require_POST
def delete_job(request, job_id):
    from django.contrib import messages
    from django.shortcuts import redirect
    
    job = get_object_or_404(Job, id=job_id)
    
    if job.employer != request.user:
        return JsonResponse({
            'success': False,
            'error': 'You do not have permission to delete this job.'
        }, status=403)
    
    try:
        job_title = job.title
        job.delete()
        
        messages.success(request, f'Job "{job_title}" has been deleted successfully.')
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


@employer_required
@require_POST
def mark_job_expired(request, job_id):
    from django.contrib import messages
    from django.shortcuts import redirect
    
    job = get_object_or_404(Job, id=job_id)
    
    if job.employer != request.user:
        return JsonResponse({
            'success': False,
            'error': 'You do not have permission to modify this job.'
        }, status=403)
    
    if job.status == 'expired':
        return JsonResponse({
            'success': False,
            'error': 'This job is already marked as expired.'
        }, status=400)
    
    try:
        from django.utils import timezone
        job.status = 'expired'
        try:
            job.expiration_date = timezone.localdate()
        except Exception:
            from datetime import date as _date
            job.expiration_date = _date.today()
        job.save()
        
        messages.success(request, f'Job "{job.title}" has been marked as expired.')
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Job "{job.title}" marked as expired.'
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
