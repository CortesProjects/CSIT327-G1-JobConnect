# dashboards/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone
from django.views.generic import ListView, TemplateView, FormView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.core.paginator import Paginator
from notifications.utils import notify_application_status_change, notify_application_shortlisted
from accounts.models import User, UserSocialLink, UserVerification
from applicant_profile.models import ApplicantProfile
from jobs.models import Job, JobApplication
from utils.mixins import EmployerRequiredMixin, ApplicantRequiredMixin
from .forms import (
    ApplicantPersonalInfoForm, 
    ApplicantProfileDetailsForm,
    ApplicantContactInfoForm,
    ApplicantProfilePrivacyForm,
    ApplicantResumeForm,
    ApplicantSocialLinkForm,
    EmployerCompanyInfoForm,
    EmployerFoundingInfoForm,
    EmployerContactInfoForm,
    EmployerBusinessPermitForm
)


class DashboardView(LoginRequiredMixin, View):
    """
    Main dashboard view that routes users to their respective dashboard
    based on user type (applicant, employer, or admin).
    """
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        if user.user_type == 'applicant':
            return self._render_applicant_dashboard(request)
        elif user.user_type == 'employer':
            return self._render_employer_dashboard(request)
        elif user.user_type == 'admin':
            return render(request, 'dashboard/admin/admin_dashboards.html')
        else:
            return render(request, 'home.html')
    
    def _render_applicant_dashboard(self, request):
        """Render applicant dashboard with stats"""
        from jobs.models import JobApplication, FavoriteJob, JobAlert
        
        user = request.user
        applied_count = JobApplication.objects.filter(applicant=user).count()
        favorite_count = FavoriteJob.objects.filter(applicant=user).count()
        alerts_count = JobAlert.objects.filter(user=user).count()
        
        # Ensure profile exists
        try:
            profile = user.profile
        except Exception:
            profile = None
        
        context = {
            'applied_count': applied_count,
            'favorite_count': favorite_count,
            'alerts_count': alerts_count,
            'profile': profile,
        }
        return render(request, 'dashboard/applicant/applicant_overview.html', context)
    
    def _render_employer_dashboard(self, request):
        """Render employer dashboard with job stats"""
        from jobs.models import Job
        from django.db.models import Count
        from dashboard.models import SavedCandidate
        
        # Fetch employer's jobs with application counts
        all_jobs = Job.objects.filter(employer=request.user)
        recent_jobs = all_jobs.annotate(
            applications_count=Count('applications')
        ).order_by('-posted_at')[:5]
        
        # Get saved candidates count
        saved_candidates_count = SavedCandidate.objects.filter(employer=request.user).count()
        
        context = {
            'has_jobs': all_jobs.exists(),
            'open_jobs_count': all_jobs.filter(status='active').count(),
            'total_jobs_count': all_jobs.count(),
            'recent_jobs': recent_jobs,
            'saved_candidates_count': saved_candidates_count,
        }
        
        return render(request, 'dashboard/employer/employer_overview.html', context)



class ApplicantJobAlertsView(ApplicantRequiredMixin, TemplateView):
    """
    Display job alerts and matching jobs for the applicant.
    Shows all user's alerts and jobs that match active alert criteria.
    """
    template_name = 'dashboard/applicant/applicant_job_alerts.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from jobs.models import FavoriteJob, JobAlert, EmploymentType, JobCategory, Job
        
        # Get user's alerts
        user_alerts = JobAlert.objects.filter(user=self.request.user).order_by('-created_at')
        
        # Get matching jobs from active alerts
        matching_jobs = self._get_matching_jobs(user_alerts)
        
        # Apply search query filter
        query = self.request.GET.get('query', '').strip()
        if query:
            matching_jobs = self._filter_jobs_by_query(matching_jobs, query)
        
        # Paginate alert jobs
        page_obj = self._paginate_jobs(matching_jobs)
        
        # Get favorited job IDs for bookmark state
        favorited_job_ids = list(
            FavoriteJob.objects.filter(applicant=self.request.user).values_list('job_id', flat=True)
        )
        
        # Get active job types and categories for the modal
        job_types = EmploymentType.objects.filter(is_active=True)
        job_categories = JobCategory.objects.filter(is_active=True)
        
        context.update({
            'user_alerts': user_alerts,
            'alert_jobs': page_obj,
            'has_configured_alerts': user_alerts.exists(),
            'favorited_job_ids': favorited_job_ids,
            'page_obj': page_obj,
            'job_types': job_types,
            'job_categories': job_categories,
            'query': query,
        })
        return context
    
    def _get_matching_jobs(self, user_alerts):
        """Get all jobs matching active alerts"""
        from jobs.models import Job
        
        matching_jobs = set()
        for alert in user_alerts.filter(is_active=True):
            try:
                # Try to use alert's get_matching_jobs method if available
                matches = alert.get_matching_jobs()
                if matches is None:
                    matches = []
                matching_jobs.update(matches)
            except Exception:
                # Fallback to manual filtering
                jobs_qs = Job.objects.filter(status='active').order_by('-posted_at')
                
                if getattr(alert, 'job_title', None):
                    jobs_qs = jobs_qs.filter(title__icontains=alert.job_title)
                if getattr(alert, 'location', None):
                    jobs_qs = jobs_qs.filter(location__icontains=alert.location)
                if getattr(alert, 'job_type', None):
                    jobs_qs = jobs_qs.filter(job_type=alert.job_type)
                if getattr(alert, 'job_category', None):
                    jobs_qs = jobs_qs.filter(category=alert.job_category)
                if getattr(alert, 'min_salary', None):
                    jobs_qs = jobs_qs.filter(min_salary__gte=alert.min_salary)
                if getattr(alert, 'max_salary', None):
                    jobs_qs = jobs_qs.filter(max_salary__lte=alert.max_salary)
                if getattr(alert, 'keywords', None):
                    for kw in [k.strip() for k in alert.keywords.split(',') if k.strip()]:
                        jobs_qs = jobs_qs.filter(
                            Q(title__icontains=kw) | Q(description__icontains=kw) | Q(tags__icontains=kw)
                        )
                
                matching_jobs.update(list(jobs_qs))
        
        # Sort by posted date (most recent first)
        return sorted(list(matching_jobs), key=lambda x: x.posted_at, reverse=True)
    
    def _filter_jobs_by_query(self, jobs, query):
        """Filter jobs by search query"""
        qlower = query.lower()
        return [
            j for j in jobs 
            if (j.title and qlower in j.title.lower()) or 
               (getattr(j, 'description', '') and qlower in j.description.lower())
        ]
    
    def _paginate_jobs(self, jobs):
        """Paginate job list"""
        from django.core.paginator import Paginator
        paginator = Paginator(jobs, 10)  # 10 jobs per page
        page_number = self.request.GET.get('page', 1)
        return paginator.get_page(page_number)


@login_required
def create_job_alert(request):
    """Create a new job alert."""
    from jobs.forms import JobAlertForm
    from django.http import JsonResponse
    
    if request.user.user_type != 'applicant':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Only applicants can create job alerts.'}, status=403)
        messages.error(request, 'Only applicants can create job alerts.')
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = JobAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.user = request.user
            alert.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Job alert created successfully!',
                    'alert_id': alert.id
                })
            
            messages.success(request, 'Job alert created successfully!')
            return redirect('dashboard:applicant_job_alerts')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
            
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobAlertForm()
    
    context = {'form': form}
    return render(request, 'dashboard/applicant/create_job_alert.html', context)


@login_required
def edit_job_alert(request, alert_id):
    """Edit an existing job alert."""
    from jobs.models import JobAlert
    from jobs.forms import JobAlertForm
    from django.http import JsonResponse
    
    alert = get_object_or_404(JobAlert, id=alert_id, user=request.user)
    
    if request.method == 'POST':
        form = JobAlertForm(request.POST, instance=alert)
        if form.is_valid():
            form.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Job alert updated successfully!'
                })
            
            messages.success(request, 'Job alert updated successfully!')
            return redirect('dashboard:applicant_job_alerts')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
            
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobAlertForm(instance=alert)
    
    context = {
        'form': form,
        'alert': alert,
        'is_edit': True
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return alert data as JSON for AJAX requests
        return JsonResponse({
            'success': True,
            'alert': {
                'id': alert.id,
                'alert_name': alert.alert_name,
                'job_title': alert.job_title,
                'location': alert.location,
                'job_type': alert.job_type.id if alert.job_type else None,
                'job_category': alert.job_category.id if alert.job_category else None,
                'min_salary': str(alert.min_salary) if alert.min_salary else '',
                'max_salary': str(alert.max_salary) if alert.max_salary else '',
                'keywords': alert.keywords,
                'is_active': alert.is_active
            }
        })
    
    return render(request, 'dashboard/applicant/create_job_alert.html', context)


@login_required
def delete_job_alert(request, alert_id):
    """Delete a job alert."""
    from jobs.models import JobAlert
    from django.http import JsonResponse
    
    alert = get_object_or_404(JobAlert, id=alert_id, user=request.user)
    
    if request.method == 'POST':
        alert.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Job alert deleted successfully!'
            })
        
        messages.success(request, 'Job alert deleted successfully!')
        return redirect('dashboard:applicant_job_alerts')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)
    
    return redirect('dashboard:applicant_job_alerts')


@login_required
def toggle_job_alert_status(request, alert_id):
    """Toggle job alert active/inactive status."""
    from jobs.models import JobAlert
    from django.http import JsonResponse
    
    alert = get_object_or_404(JobAlert, id=alert_id, user=request.user)
    
    if request.method == 'POST':
        alert.is_active = not alert.is_active
        alert.save()
        
        status_text = 'activated' if alert.is_active else 'deactivated'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'is_active': alert.is_active,
                'message': f'Job alert {status_text} successfully!'
            })
        
        messages.success(request, f'Job alert {status_text} successfully!')
        return redirect('dashboard:applicant_job_alerts')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)
    
    return redirect('dashboard:applicant_job_alerts')

@login_required
def applicant_settings(request):
    from applicant_profile.models import NotificationPreferences
    from django.contrib.auth import authenticate
    
    profile = get_object_or_404(ApplicantProfile, user=request.user)
    
    # Get or create notification preferences
    notification_prefs, created = NotificationPreferences.objects.get_or_create(
        user=request.user,
        defaults={
            'notify_shortlisted': True,
            'notify_applications': True,
            'notify_job_alerts': True
        }
    )
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'personal_info':
            form = ApplicantPersonalInfoForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Personal information updated successfully!')
                    return redirect('dashboard:applicant_settings')
                except Exception as e:
                    messages.error(request, f'Error saving personal information: {str(e)}')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
                messages.error(request, 'Please correct the errors below.')
        
        elif form_type == 'profile_details':
            form = ApplicantProfileDetailsForm(request.POST, instance=profile)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Profile details updated successfully!')
                    return redirect('dashboard:applicant_settings')
                except Exception as e:
                    messages.error(request, f'Error saving profile details: {str(e)}')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
                messages.error(request, 'Please correct the errors below.')
        
        elif form_type == 'social_links_bulk':
            try:
                # Get arrays from POST data
                platforms = request.POST.getlist('platform[]')
                urls = request.POST.getlist('url[]')
                link_ids = request.POST.getlist('link_id[]')
                
                # Get existing social link IDs for this user
                existing_ids = set(request.user.social_links.values_list('id', flat=True))
                submitted_ids = set()
                
                # Process each submitted link
                for i, (platform, url) in enumerate(zip(platforms, urls)):
                    if not platform or not url:
                        continue
                    
                    link_id = link_ids[i] if i < len(link_ids) and link_ids[i] else None
                    
                    if link_id:
                        # Update existing link
                        link_id = int(link_id)
                        submitted_ids.add(link_id)
                        social_link = UserSocialLink.objects.filter(id=link_id, user=request.user).first()
                        if social_link:
                            social_link.platform = platform
                            social_link.url = url
                            social_link.save()
                    else:
                        # Create new link
                        social_link = UserSocialLink.objects.create(
                            user=request.user,
                            platform=platform,
                            url=url
                        )
                        submitted_ids.add(social_link.id)
                
                # Delete links that were removed (in existing but not in submitted)
                ids_to_delete = existing_ids - submitted_ids
                if ids_to_delete:
                    UserSocialLink.objects.filter(id__in=ids_to_delete, user=request.user).delete()
                
                messages.success(request, 'Social links updated successfully!')
                return redirect('dashboard:applicant_settings')
            except Exception as e:
                messages.error(request, f'Error updating social links: {str(e)}')
        
        elif form_type == 'social_link':
            social_link_id = request.POST.get('social_link_id')
            if social_link_id:
                # Edit existing social link
                social_link = get_object_or_404(UserSocialLink, id=social_link_id, user=request.user)
                form = ApplicantSocialLinkForm(request.POST, instance=social_link)
            else:
                # Add new social link
                form = ApplicantSocialLinkForm(request.POST)
            
            if form.is_valid():
                social_link = form.save(commit=False)
                social_link.user = request.user
                social_link.save()
                messages.success(request, 'Social link saved successfully!')
                return redirect('dashboard:applicant_settings')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif form_type == 'delete_social_link':
            social_link_id = request.POST.get('social_link_id')
            social_link = get_object_or_404(UserSocialLink, id=social_link_id, user=request.user)
            social_link.delete()
            messages.success(request, 'Social link deleted successfully!')
            return redirect('dashboard:applicant_settings')
        
        elif form_type == 'contact_info':
            form = ApplicantContactInfoForm(request.POST, instance=profile, user=request.user)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Contact information updated successfully!')
                    return redirect('dashboard:applicant_settings')
                except Exception as e:
                    messages.error(request, f'Error saving contact information: {str(e)}')
            else:
                for field, errors in form.errors.items():
                    field_label = form.fields.get(field).label if field in form.fields else field
                    for error in errors:
                        messages.error(request, f'{field_label}: {error}')
        
        elif form_type == 'profile_privacy':
            form = ApplicantProfilePrivacyForm(request.POST, instance=profile)
            if form.is_valid():
                try:
                    form.save()
                    status = 'public' if form.cleaned_data['is_public'] else 'private'
                    messages.success(request, f'Profile privacy set to {status}!')
                    return redirect('dashboard:applicant_settings')
                except Exception as e:
                    messages.error(request, f'Error saving privacy settings: {str(e)}')
            else:
                for field, errors in form.errors.items():
                    field_label = form.fields.get(field).label if field in form.fields else field
                    for error in errors:
                        messages.error(request, f'{field_label}: {error}')
        
        elif form_type == 'resume':
            form = ApplicantResumeForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Resume uploaded successfully!')
                    return redirect('dashboard:applicant_settings')
                except Exception as e:
                    messages.error(request, f'Error uploading resume: {str(e)}')
            else:
                for field, errors in form.errors.items():
                    field_label = form.fields.get(field).label if field in form.fields else field
                    for error in errors:
                        messages.error(request, f'{field_label}: {error}')
        
        elif form_type == 'change_password':
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                try:
                    user = password_form.save()
                    update_session_auth_hash(request, user)  # Keep user logged in
                    messages.success(request, 'Password changed successfully!')
                    return redirect('dashboard:applicant_settings')
                except Exception as e:
                    messages.error(request, f'Error changing password: {str(e)}')
            else:
                # Display password form errors with field labels
                for field, errors in password_form.errors.items():
                    field_label = password_form.fields.get(field).label if field in password_form.fields else field
                    for error in errors:
                        messages.error(request, f'{field_label}: {error}')
        
        elif form_type == 'notification_preferences':
            # Update notification preferences
            notification_prefs.notify_shortlisted = request.POST.get('notify_shortlisted') == 'on'
            notification_prefs.notify_applications = request.POST.get('notify_applications') == 'on'
            notification_prefs.notify_job_alerts = request.POST.get('notify_job_alerts') == 'on'
            notification_prefs.save()
            messages.success(request, 'Notification preferences updated successfully!')
            return redirect('dashboard:applicant_settings')
        
        elif form_type == 'delete_account':
            # Verify password
            password = request.POST.get('password')
            user = authenticate(username=request.user.username, password=password)
            
            if user is not None:
                try:
                    # Delete user account (cascades to profile and related data)
                    username = request.user.username
                    request.user.delete()
                    messages.success(request, f'Account {username} has been permanently deleted.')
                    return redirect('home')
                except Exception as e:
                    messages.error(request, f'Error deleting account: {str(e)}')
            else:
                messages.error(request, 'Incorrect password. Account deletion cancelled.')
                return redirect('dashboard:applicant_settings')
    
    # Initialize all forms with current data. For password form, only create
    # an unbound form here if it hasn't been created/overwritten during POST
    personal_info_form = ApplicantPersonalInfoForm(instance=profile)
    profile_details_form = ApplicantProfileDetailsForm(instance=profile)
    contact_info_form = ApplicantContactInfoForm(instance=profile, user=request.user)
    profile_privacy_form = ApplicantProfilePrivacyForm(instance=profile)
    resume_form = ApplicantResumeForm(instance=profile)
    # password_form may be set during POST handling to the bound form with errors
    if 'password_form' not in locals():
        password_form = PasswordChangeForm(request.user)
    social_link_form = ApplicantSocialLinkForm()
    
    # Get existing social links for this user
    social_links = request.user.social_links.all()
    
    context = {
        'profile': profile,
        'personal_info_form': personal_info_form,
        'profile_details_form': profile_details_form,
        'contact_info_form': contact_info_form,
        'profile_privacy_form': profile_privacy_form,
        'resume_form': resume_form,
        'password_form': password_form,
        'social_link_form': social_link_form,
        'social_links': social_links,
        'notification_prefs': notification_prefs,
    }
    
    return render(request, 'dashboard/applicant/applicant_settings.html', context)


class PublicEmployerProfileView(TemplateView):
    """
    Display public employer profile (read-only view).
    No login required - accessible to anyone.
    Shows only active jobs and hides sensitive statistics.
    """
    template_name = 'dashboard/employer/employer_profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from jobs.models import Job
        from django.db.models import Count
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        employer_id = kwargs.get('employer_id')
        
        # Get employer user
        employer = get_object_or_404(User, id=employer_id, user_type='employer')
        
        # Get employer profile
        try:
            profile = employer.employer_profile_rel
        except:
            profile = None
        
        # Get social links
        social_links = UserSocialLink.objects.filter(user=employer).order_by('platform')
        
        # Get recent jobs with application counts (only active jobs for public view)
        recent_jobs = Job.objects.filter(
            employer=employer,
            status='active'
        ).select_related(
            'category',
            'job_type',
            'education',
            'experience',
            'job_level',
            'salary_type'
        ).annotate(
            applications_count=Count('applications')
        ).order_by('-posted_at')[:3]
        
        # Calculate statistics (public view - only show active jobs)
        total_jobs = Job.objects.filter(employer=employer, status='active').count()
        active_jobs = total_jobs
        total_applications = 0  # Hide application stats for public view
        hired_count = 0  # Hide hiring stats for public view
        
        context.update({
            'profile': profile,
            'social_links': social_links,
            'recent_jobs': recent_jobs,
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'total_applications': total_applications,
            'hired_count': hired_count,
            'is_owner': False,
            'profile_employer': employer,
        })
        return context


@login_required
def employer_job_applications(request, job_id):
    """Show applications for a specific job posting (employer-only)."""
    from django.shortcuts import get_object_or_404
    from django.core.exceptions import PermissionDenied
    from jobs.models import Job, ApplicationStage, JobApplication
    from django.db import models
    from django.db.models import Prefetch
    from dashboard.forms import EmployerApplicationFilterForm

    # Ensure user is an employer
    if getattr(request.user, 'user_type', None) != 'employer':
        messages.error(request, 'Access denied. Employer account required.')
        return redirect('dashboard:dashboard')

    # Ensure the job exists and belongs to the current employer
    job = get_object_or_404(Job, id=job_id)
    if job.employer_id != request.user.id:
        raise PermissionDenied("You do not have permission to view these applications.")

    # Handle POST requests for stage management
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        stage_name = request.POST.get('stage_name', '').strip()
        stage_id = request.POST.get('stage_id')

        # Add new stage
        if form_type == 'add_stage' and stage_name:
            # Get max order for this job
            max_order = ApplicationStage.objects.filter(job=job).aggregate(
                models.Max('order')
            )['order__max'] or 0
            
            ApplicationStage.objects.create(
                job=job,
                name=stage_name,
                order=max_order + 1
            )
            messages.success(request, f'Column "{stage_name}" added.')
            # Preserve querystring when redirecting back
            return redirect(request.get_full_path())

        # Edit existing stage
        if form_type == 'edit_stage' and stage_id and stage_name:
            try:
                stage = ApplicationStage.objects.get(id=stage_id, job=job)
                if stage.is_system:
                    messages.error(request, 'Cannot edit system-generated columns.')
                else:
                    stage.name = stage_name
                    stage.save()
                    messages.success(request, f'Column "{stage_name}" updated.')
            except ApplicationStage.DoesNotExist:
                messages.error(request, 'Stage not found.')
            return redirect(request.get_full_path())

        # Delete stage
        if form_type == 'delete_stage' and stage_id:
            try:
                stage = ApplicationStage.objects.get(id=stage_id, job=job)
                if stage.is_system:
                    messages.error(request, 'Cannot delete system-generated columns.')
                else:
                    # Move applications in this stage back to null (All Applications)
                    JobApplication.objects.filter(stage=stage).update(stage=None)
                    stage.delete()
                    messages.success(request, 'Column deleted. Applications moved to "All Applications".')
            except ApplicationStage.DoesNotExist:
                messages.error(request, 'Stage not found.')
            return redirect(request.get_full_path())

    # Education and experience choices come from applicant profile model
    from applicant_profile.models import ApplicantProfile
    education_choices = list(getattr(ApplicantProfile, 'EDUCATION_LEVEL_CHOICES', []))

    try:
        experience_field = ApplicantProfile._meta.get_field('experience')
        experience_choices = list(experience_field.choices)
    except Exception:
        experience_choices = []

    # Initialize filter form with GET parameters and dynamic choices (only education/experience)
    filter_form = EmployerApplicationFilterForm(
        request.GET or None,
        education_choices=education_choices,
        experience_choices=experience_choices,
    )

    # Base queryset for applications for this job (will be filtered below)
    base_qs = JobApplication.objects.filter(job=job).select_related(
        'applicant',
        'applicant__applicant_profile_rel'
    )

    # Apply education/experience filters and sorting from validated form
    if filter_form.is_valid():
        cd = filter_form.cleaned_data
        education_val = cd.get('education')
        if education_val:
            base_qs = base_qs.filter(applicant__applicant_profile_rel__education_level=education_val)

        experience_val = cd.get('experience')
        if experience_val:
            base_qs = base_qs.filter(applicant__applicant_profile_rel__experience=experience_val)

        # Server-side sorting
        sort_val = cd.get('sort', '').strip()
        if sort_val == 'oldest':
            base_qs = base_qs.order_by('application_date')
        elif sort_val == 'name':
            base_qs = base_qs.order_by('applicant__first_name', 'applicant__last_name')
        else:  # 'newest' or default
            base_qs = base_qs.order_by('-application_date')
    else:
        base_qs = base_qs.order_by('-application_date')

    # Split into columns: All Applications (stage is null) and stages
    all_applications = base_qs.filter(stage__isnull=True)

    # Use Prefetch with the filtered base_qs so each stage's applications reflect filters
    prefetch_apps = Prefetch('applications', queryset=base_qs)

    custom_stages = ApplicationStage.objects.filter(
        job=job,
        is_system=False
    ).prefetch_related(prefetch_apps).order_by('order', 'created_at')

    system_stages = ApplicationStage.objects.filter(
        job=job,
        is_system=True
    ).prefetch_related(prefetch_apps).order_by('order', 'created_at')

    context = {
        'job': job,
        'all_applications': all_applications,
        'custom_columns': custom_stages,
        'system_columns': system_stages,
        'filter_form': filter_form,
        'education_choices': education_choices,
        'experience_choices': experience_choices,
    }
    return render(request, 'dashboard/employer/employer_job_applications.html', context)

@login_required
def employer_candidate_detail(request, application_id):
    """Display detailed information about a candidate/applicant for a specific job application."""
    from django.shortcuts import get_object_or_404
    from django.core.exceptions import PermissionDenied
    from jobs.models import JobApplication
    from dashboard.models import SavedCandidate
    
    # Ensure user is an employer
    if getattr(request.user, 'user_type', None) != 'employer':
        messages.error(request, 'Access denied. Employer account required.')
        return redirect('dashboard:dashboard')
    
    # Fetch the application with related data
    application = get_object_or_404(
        JobApplication.objects.select_related(
            'applicant',
            'applicant__applicant_profile_rel',
            'job'
        ),
        id=application_id
    )
    
    # Verify the employer owns the job this application is for
    if application.job.employer_id != request.user.id:
        raise PermissionDenied("You do not have permission to view this candidate.")
    
    # Get applicant profile
    profile = application.applicant.applicant_profile_rel
    
    # Get social links
    social_links = application.applicant.social_links.all()
    
    # Check if candidate is saved
    is_saved = SavedCandidate.objects.filter(
        employer=request.user,
        application=application
    ).exists()
    
    context = {
        'application': application,
        'applicant': application.applicant,
        'profile': profile,
        'social_links': social_links,
        'job': application.job,
        'is_saved': is_saved,
    }
    
    return render(request, 'dashboard/employer/employer_candidate_detail.html', context)


@login_required
def hire_candidate(request, application_id):
    """Hire a candidate - creates/moves to Hired stage and updates application status."""
    from django.shortcuts import get_object_or_404
    from django.core.exceptions import PermissionDenied
    from jobs.models import JobApplication, ApplicationStage
    from django.db import models
    
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('dashboard:dashboard')
    
    # Ensure user is an employer
    if getattr(request.user, 'user_type', None) != 'employer':
        messages.error(request, 'Access denied. Employer account required.')
        return redirect('dashboard:dashboard')
    
    try:
        # Fetch the application
        application = get_object_or_404(
            JobApplication.objects.select_related('job'),
            id=application_id
        )
        
        # Verify employer owns this job
        if application.job.employer_id != request.user.id:
            raise PermissionDenied("You do not have permission to hire this candidate.")
        
        # Get or create "Hired" stage with is_system=True flag
        hired_stage, created = ApplicationStage.objects.get_or_create(
            job=application.job,
            name='Hired',
            defaults={
                'order': 9999,  # Put at the end
                'is_system': True  # Mark as system-generated
            }
        )
        
        # Update application
        application.stage = hired_stage
        application.status = 'hired'
        application.hired_date = timezone.now().date()
        application.save()
        
        messages.success(request, f'Successfully hired {application.applicant.applicant_profile_rel.full_name or application.applicant.email}!')
        return redirect('dashboard:employer_job_applications', job_id=application.job.id)
        
    except Exception as e:
        messages.error(request, f'Error hiring candidate: {str(e)}')
        return redirect('dashboard:employer_candidate_detail', application_id=application_id)


@login_required
def toggle_save_candidate(request, application_id):
    """Toggle save/unsave status for a candidate"""
    from django.shortcuts import get_object_or_404
    from django.core.exceptions import PermissionDenied
    from jobs.models import JobApplication
    from dashboard.models import SavedCandidate
    
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('dashboard:dashboard')
    
    # Ensure user is an employer
    if getattr(request.user, 'user_type', None) != 'employer':
        messages.error(request, 'Access denied. Employer account required.')
        return redirect('dashboard:dashboard')
    
    try:
        # Fetch the application
        application = get_object_or_404(
            JobApplication.objects.select_related('job'),
            id=application_id
        )
        
        # Verify employer owns this job
        if application.job.employer_id != request.user.id:
            messages.error(request, 'You do not have permission to save this candidate.')
            return redirect('dashboard:dashboard')
        
        # Toggle save status
        saved_candidate, created = SavedCandidate.objects.get_or_create(
            employer=request.user,
            application=application
        )
        
        if not created:
            # Already saved, so unsave it
            saved_candidate.delete()
            messages.success(request, 'Candidate removed from saved list.')
        else:
            # Newly saved
            messages.success(request, 'Candidate saved successfully!')
        
        # Redirect back to the referring page
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        else:
            return redirect('dashboard:employer_candidate_detail', application_id=application_id)
        
    except PermissionDenied:
        messages.error(request, 'You do not have permission to save this candidate.')
        return redirect('dashboard:dashboard')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        else:
            return redirect('dashboard:dashboard')

@login_required
def move_application_stage(request, application_id):
    """Move an application to a different stage (for drag-and-drop persistence)."""
    from django.shortcuts import get_object_or_404
    from django.core.exceptions import PermissionDenied
    from django.http import JsonResponse
    from jobs.models import JobApplication, ApplicationStage
    
    # Only accept POST
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)
    
    # Ensure user is an employer
    if getattr(request.user, 'user_type', None) != 'employer':
        return JsonResponse({'success': False, 'error': 'Employer access required'}, status=403)
    
    try:
        application = get_object_or_404(
            JobApplication.objects.select_related('job'),
            id=application_id
        )
        
        # Verify employer owns this job
        if application.job.employer_id != request.user.id:
            raise PermissionDenied("You do not have permission to modify this application.")
        
        # Get target stage from POST data
        stage_id = request.POST.get('stage_id')
        
        if stage_id == '' or stage_id == 'null' or stage_id is None:
            # Move to "All Applications" (no stage)
            application.stage = None
        else:
            # Move to specific stage
            stage = get_object_or_404(
                ApplicationStage,
                id=stage_id,
                job=application.job
            )
            application.stage = stage
        
        application.save()
        
        # Notify applicant about stage change if moved to a significant stage
        if stage and stage.name.lower() in ['shortlisted', 'interview', 'offer']:
            if stage.name.lower() == 'shortlisted':
                notify_application_shortlisted(application.applicant, application.job, application)
            else:
                notify_application_status_change(application.applicant, application.job, stage.name.lower())

        response_data = {
            'success': True,
            'message': 'Application moved successfully',
            'stage_name': application.stage.name if application.stage else 'All Applications'
        }

        # If the request is an AJAX/XHR request, return JSON so client JS can consume it.
        # Otherwise this was submitted as a normal form POST; redirect back and use
        # Django messages so the browser doesn't render raw JSON.
        is_xhr = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
        if is_xhr:
            return JsonResponse(response_data)

        # Non-AJAX: set a success message and redirect back to the employer applications page
        messages.success(request, response_data['message'])
        return redirect(reverse('dashboard:employer_job_applications', args=[application.job.id]))
        
    except Exception as e:
        # For AJAX requests return JSON error payload; for normal POSTs set an error message
        # and redirect back so the user sees the message instead of raw JSON.
        is_xhr = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
        if is_xhr:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

        messages.error(request, f'Error moving application: {str(e)}')
        # Try to redirect back to referrer or to the employer job applications listing
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('dashboard:dashboard')

#------------------------------------------
#              Admin Stuff
#------------------------------------------
@login_required
def admin_dashboards(request):
    # Count verified employers (those with verification status = 'verified')
    total_verified_employers = UserVerification.objects.filter(
        user__user_type='employer',
        status='verified'
    ).count()
    
    # Count pending/unverified employers (pending or no verification record)
    total_unverified_employers = User.objects.filter(
        user_type='employer'
    ).exclude(
        verification__status='verified'
    ).count()
    
    total_applicants = User.objects.filter(user_type='applicant').count()
    
    # Optional: count active job postings if needed
    total_job_postings = Job.objects.filter(status='active').count()

    context = {
        'total_verified_employers': total_verified_employers,
        'total_unverified_employers': total_unverified_employers,
        'total_applicants': total_applicants,
        'total_job_postings': total_job_postings,
    }
    return render(request, 'dashboard/admin/admin_dashboards.html', context)

@login_required
def admin_total_employers_verified(request):
    verified_employers = User.objects.filter(
        user_type='employer',
        verification__status='verified'
    ).select_related('employer_profile_rel', 'verification')

    context = {
        'verified_employers': verified_employers,
    }
    return render(request, "dashboard/admin/admin_total_employers_verified.html", context)

@login_required
def admin_accept_reject_employer(request):
    # Show employers that are pending or have no verification record yet
    unverified_employers = User.objects.filter(
        user_type='employer'
    ).exclude(
        verification__status='verified'
    ).select_related('employer_profile_rel').prefetch_related('verification')

    context = {
        'unverified_employers': unverified_employers
    }
    return render(request, 'dashboard/admin/admin_accept_reject_employer.html', context)

@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')  # Only admins can approve
def approve_employer(request, employer_id):
    if request.method == 'POST':
        employer = get_object_or_404(User, id=employer_id, user_type='employer')
        
        # Create or update verification record
        verification, created = UserVerification.objects.get_or_create(
            user=employer,
            defaults={
                'admin_verifier': request.user,
                'status': 'verified',
                'verification_date': timezone.now(),
                'notes': 'Approved by admin'
            }
        )
        
        if not created:
            verification.admin_verifier = request.user
            verification.status = 'verified'
            verification.verification_date = timezone.now()
            verification.notes = 'Approved by admin'
            verification.save()
        
        messages.success(request, f'Employer {employer.email} has been verified successfully.')
    
    return redirect('dashboard:admin_accept_reject_employer')

@login_required
@user_passes_test(lambda u: u.user_type == 'ADMIN')  # Only admins can reject
def reject_employer(request, employer_id):
    if request.method == 'POST':
        employer = get_object_or_404(User, id=employer_id, user_type='employer')
        rejection_note = request.POST.get('rejection_note', 'Rejected by admin')
        
        # Create or update verification record
        verification, created = UserVerification.objects.get_or_create(
            user=employer,
            defaults={
                'admin_verifier': request.user,
                'status': 'rejected',
                'verification_date': timezone.now(),
                'notes': rejection_note
            }
        )
        
        if not created:
            verification.admin_verifier = request.user
            verification.status = 'rejected'
            verification.verification_date = timezone.now()
            verification.notes = rejection_note
            verification.save()
        
        messages.warning(request, f'Employer {employer.email} has been rejected.')
    
    return redirect('dashboard:admin_accept_reject_employer')

@login_required
def admin_applicants(request):
    applicants = User.objects.filter(user_type='applicant')
    context = {'applicants': applicants}
    return render(request, 'dashboard/admin/admin_applicants.html', context)

@login_required
def admin_applicant_detail(request, applicant_id):
    applicant = get_object_or_404(User, id=applicant_id, user_type='applicant')
    profile = getattr(applicant, 'applicant_profile_rel', None)
    application = JobApplication.objects.filter(applicant=applicant).last()
    social_links = UserSocialLink.objects.filter(user=applicant)
    is_saved = False
    
    context = {
        'applicant': applicant,
        'profile': profile,
        'application': application,
        'social_links': social_links,
        'is_saved': is_saved,
    }
    
    return render(request, 'dashboard/admin/admin_candidate_detail.html', context)

@login_required
def admin_job_postings(request):
    # Only show jobs with status 'active' (lowercase)
    active_jobs = Job.objects.filter(status__in=['active', 'expired']).order_by('-posted_at')

    context = {
        'active_jobs': active_jobs
    }
    return render(request, "dashboard/admin/admin_job_postings.html", context)

@login_required
def admin_job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Only admins can access
    if not request.user.is_staff:
        return redirect('accounts:login')

    context = {
        'job': job,
        'can_edit_job': True,  # or your logic
    }
    return render(request, "dashboard/admin/admin_job_detail.html", context)

#------------------------------------------
#          Admin Stuff Ends Here
# -----------------------------------------


#------------------------------------------
#          Class-Based Views
# -----------------------------------------

class EmployerJobListView(EmployerRequiredMixin, ListView):
    """
    Displays list of jobs posted by the current employer.
    Allows filtering by job status (active, expired).
    """
    model = Job
    template_name = 'dashboard/employer/employer_my_jobs.html'
    context_object_name = 'all_jobs'

    def get_queryset(self):
        from django.db.models import Count
        
        queryset = Job.objects.filter(
            employer=self.request.user
        ).select_related(
            'category',
            'job_type',
            'education',
            'experience',
            'job_level',
            'salary_type'
        ).annotate(
            applications_count=Count('applications')
        ).order_by('-posted_at')
        
        status_filter = self.request.GET.get('status', 'all')
        if status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['status_filter'] = self.request.GET.get('status', 'all')
        context['has_jobs'] = queryset.exists()
        context['total_jobs'] = queryset.count()
        return context


class ApplicantJobSearchView(ApplicantRequiredMixin, ListView):
    """
    Search jobs for applicants with filters using Django form validation.
    Matches the logic of the original applicant_search_jobs function-based view.
    """
    model = Job
    template_name = 'dashboard/applicant/applicant_search_jobs.html'
    context_object_name = 'jobs'
    paginate_by = 10

    def get_queryset(self):
        from jobs.models import JobCategory, EducationLevel, ExperienceLevel, JobLevel
        from dashboard.forms import JobSearchForm
        from django.db.models import Q, Count
        
        # Get filter options from lookup tables (only active items)
        all_categories = JobCategory.objects.filter(is_active=True)
        all_educations = EducationLevel.objects.filter(is_active=True)
        all_experiences = ExperienceLevel.objects.filter(is_active=True)
        all_job_levels = JobLevel.objects.filter(is_active=True)
        
        # Prepare choices for form fields
        category_choices = [('', 'Category')] + [(str(c.id), c.name) for c in all_categories]
        education_choices = [('', 'Education')] + [(str(e.id), e.name) for e in all_educations]
        experience_choices = [('', 'Experience')] + [(str(e.id), e.name) for e in all_experiences]
        job_level_choices = [('', 'Level')] + [(str(j.id), j.name) for j in all_job_levels]
        
        # Initialize form with GET data and dynamic choices
        self.form = JobSearchForm(
            self.request.GET or None,
            category_choices=category_choices,
            education_choices=education_choices,
            experience_choices=experience_choices,
            job_level_choices=job_level_choices
        )
        
        # Start with active jobs only with optimized queries
        jobs = Job.objects.filter(status='active').select_related(
            'employer',
            'category',
            'job_type',
            'education',
            'experience',
            'job_level',
            'salary_type'
        ).annotate(applications_count=Count('applications'))
        
        # Apply filters only if form is valid
        if self.form.is_valid():
            cleaned_data = self.form.cleaned_data
            
            # Keyword search
            query = cleaned_data.get('query')
            if query:
                # Search title, description, company name, and tags field
                jobs = jobs.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(company_name__icontains=query) |
                    Q(tags__icontains=query)
                ).distinct()
            
            # Category filter (single-select)
            category_val = cleaned_data.get('category')
            if category_val:
                jobs = jobs.filter(category_id=category_val)
            
            # Education filter (single-select)
            education_val = cleaned_data.get('education')
            if education_val:
                jobs = jobs.filter(education_id=education_val)
            
            # Experience filter (single-select)
            experience_val = cleaned_data.get('experience')
            if experience_val:
                jobs = jobs.filter(experience_id=experience_val)
            
            # Job level filter (single-select)
            job_level_val = cleaned_data.get('job_level')
            if job_level_val:
                jobs = jobs.filter(job_level_id=job_level_val)
            
            # Salary filter
            salary_min = cleaned_data.get('salary_min')
            if salary_min:
                jobs = jobs.filter(min_salary__gte=salary_min)
            
            salary_max = cleaned_data.get('salary_max')
            if salary_max:
                jobs = jobs.filter(max_salary__lte=salary_max)
        
        # Order by most recent
        return jobs.order_by('-posted_at')

    def get_context_data(self, **kwargs):
        from jobs.models import JobCategory, EducationLevel, ExperienceLevel, JobLevel, FavoriteJob
        
        context = super().get_context_data(**kwargs)
        
        # Add the form to context
        context['form'] = self.form
        
        # Get filter options from lookup tables (only active items)
        context['categories'] = JobCategory.objects.filter(is_active=True)
        context['educations'] = EducationLevel.objects.filter(is_active=True)
        context['experiences'] = ExperienceLevel.objects.filter(is_active=True)
        context['job_levels'] = JobLevel.objects.filter(is_active=True)
        
        # Get favorited job IDs for the current applicant
        context['favorited_job_ids'] = list(
            FavoriteJob.objects.filter(applicant=self.request.user).values_list('job_id', flat=True)
        )
        
        return context


class ApplicantFavoriteJobsView(ApplicantRequiredMixin, ListView):
    """
    Show favorite jobs for the current applicant.
    Template expects 'favorites' to be a page of FavoriteJob objects so it can use
    favorite.job inside each loop. Matches the original applicant_favorite_jobs function-based view.
    """
    model = None  # We'll set the queryset directly
    template_name = 'dashboard/applicant/applicant_favorite_jobs.html'
    context_object_name = 'favorites'
    paginate_by = 10

    def get_queryset(self):
        from jobs.models import FavoriteJob
        
        # Query: applicant's favorites, with related Job data for efficiency
        favorites_qs = FavoriteJob.objects.filter(
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
        
        return favorites_qs

    def get_context_data(self, **kwargs):
        from jobs.models import FavoriteJob
        
        context = super().get_context_data(**kwargs)
        
        # Single count to avoid repeated DB hits in template
        favorites_qs = self.get_queryset()
        context['favorite_count'] = favorites_qs.count()
        
        # Job ID lists (keeps compatibility with existing templates/JS)
        context['favorited_job_ids'] = list(favorites_qs.values_list('job_id', flat=True))
        context['favorited_job_ids_page'] = list(
            context['page_obj'].object_list.values_list('job_id', flat=True)
        )
        
        return context


class ApplicantAppliedJobsListView(ApplicantRequiredMixin, ListView):
    """
    Display all job applications submitted by the current applicant.
    Shows application status, date applied, and job details.
    """
    model = JobApplication
    template_name = 'dashboard/applicant/applicant_applied_jobs.html'
    context_object_name = 'applied_jobs'
    paginate_by = 10
    
    def get_queryset(self):
        return JobApplication.objects.filter(
            applicant=self.request.user
        ).select_related(
            'job',
            'job__employer',
            'job__employer__employer_profile_rel',
            'job__category',
            'job__job_type',
            'job__education',
            'job__experience',
            'job__job_level'
        ).order_by('-application_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application_count'] = self.get_queryset().count()
        return context


class EmployerPostJobView(EmployerRequiredMixin, FormView):
    """
    Handle job posting creation.
    Matches the logic of the original employer_post_job function-based view.
    """
    template_name = 'dashboard/employer/employer_post_job.html'
    form_class = None  # Will be set dynamically
    
    def dispatch(self, request, *args, **kwargs):
        # Get employer profile and verify company name exists
        try:
            self.employer_profile = request.user.employer_profile_rel
            if not self.employer_profile.company_name:
                messages.warning(request, 'Please complete your company profile before posting a job.')
                return redirect('dashboard:employer_settings')
        except:
            messages.error(request, 'Please complete your profile setup first.')
            return redirect('dashboard:employer_settings')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_class(self):
        from jobs.forms import JobPostForm
        return JobPostForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = self.employer_profile.company_name if self.employer_profile else ''
        return context
    
    def form_valid(self, form):
        try:
            job = form.save(commit=False)
            job.employer = self.request.user
            job.company_name = self.employer_profile.company_name
            job.status = 'active'
            job.save()
            
            # Redirect with success query parameter
            return redirect(f"{reverse('dashboard:employer_post_job')}?success=true")
        except Exception as e:
            messages.error(self.request, f'Error posting job: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        # Do not push per-field errors to messages container; render form with inline errors
        return super().form_invalid(form)


class EmployerSavedCandidatesView(EmployerRequiredMixin, ListView):
    """
    Display all saved candidates for the employer.
    Matches the logic of the original employer_saved_candidates function-based view.
    """
    template_name = 'dashboard/employer/employer_saved_candidates.html'
    context_object_name = 'saved_candidates'
    
    def get_queryset(self):
        from dashboard.models import SavedCandidate
        
        # Get all saved candidates with related data
        return SavedCandidate.objects.filter(
            employer=self.request.user
        ).select_related(
            'application',
            'application__applicant',
            'application__applicant__applicant_profile_rel',
            'application__job'
        ).order_by('-saved_at')


class EmployerEditJobView(EmployerRequiredMixin, UpdateView):
    """
    Handle job editing (limited to 7 days after posting).
    Matches the logic of the original employer_edit_job function-based view.
    """
    model = Job
    template_name = 'dashboard/employer/employer_post_job.html'
    pk_url_kwarg = 'job_id'
    
    def dispatch(self, request, *args, **kwargs):
        # Get job and verify ownership
        self.object = self.get_object()
        
        if self.object.employer != request.user:
            messages.error(request, 'You do not have permission to edit this job.')
            return redirect('dashboard:employer_my_jobs')
        
        # Check 7-day edit window
        days_since_posted = (timezone.now() - self.object.posted_at).days
        
        # Disallow edits if the job is already marked expired
        if self.object.status == 'expired':
            messages.error(request, 'This job has been marked as expired and can no longer be edited.')
            return redirect('jobs:job_detail', job_id=self.object.id)
        
        if days_since_posted > 7:
            messages.error(request, f'You can only edit jobs within 7 days of posting. This job was posted {days_since_posted} days ago.')
            return redirect('jobs:job_detail', job_id=self.object.id)
        
        # Get employer profile
        try:
            self.employer_profile = request.user.employer_profile_rel
        except:
            messages.error(request, 'Please complete your profile setup first.')
            return redirect('dashboard:employer_settings')
        
        # Store days_since_posted for context
        self.days_since_posted = days_since_posted
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_class(self):
        from jobs.forms import JobPostForm
        return JobPostForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        context['job'] = self.object
        context['company_name'] = self.employer_profile.company_name if self.employer_profile else ''
        context['days_since_posted'] = self.days_since_posted
        context['days_remaining'] = 7 - self.days_since_posted
        return context
    
    def form_valid(self, form):
        try:
            updated_job = form.save(commit=False)
            updated_job.employer = self.request.user
            updated_job.company_name = self.employer_profile.company_name
            # Don't change the posted_at date or status during edit
            updated_job.save()
            
            messages.success(self.request, f'Job "{updated_job.title}" has been updated successfully!')
            return redirect('jobs:job_detail', job_id=updated_job.id)
        except Exception as e:
            messages.error(self.request, f'Error updating job: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        # Form has validation errors, will be displayed inline
        return super().form_invalid(form)


class EmployerSettingsView(EmployerRequiredMixin, TemplateView):
    """
    Employer settings page handling multiple forms:
    - Company info, founding info, contact info, business permit
    - Password change, social links management
    Matches the logic of the original employer_settings function-based view.
    """
    template_name = 'dashboard/employer/employer_settings.html'
    
    def get_context_data(self, **kwargs):
        from employer_profile.models import EmployerProfile
        
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(EmployerProfile, user=self.request.user)
        
        # Initialize all forms with current data
        context['profile'] = profile
        context['company_info_form'] = EmployerCompanyInfoForm(instance=profile)
        context['founding_info_form'] = EmployerFoundingInfoForm(instance=profile)
        context['contact_info_form'] = EmployerContactInfoForm(instance=profile, user=self.request.user)
        context['business_permit_form'] = EmployerBusinessPermitForm(instance=profile)
        context['password_form'] = PasswordChangeForm(user=self.request.user)
        context['social_link_form'] = ApplicantSocialLinkForm()
        context['social_links'] = self.request.user.social_links.all()
        
        return context
    
    def post(self, request, *args, **kwargs):
        from employer_profile.models import EmployerProfile
        
        profile = get_object_or_404(EmployerProfile, user=request.user)
        form_type = request.POST.get('form_type')
        
        if form_type == 'company_info':
            form = EmployerCompanyInfoForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Company information updated successfully!')
                return redirect('dashboard:employer_settings')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif form_type == 'founding_info':
            form = EmployerFoundingInfoForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Founding information updated successfully!')
                return redirect('dashboard:employer_settings')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif form_type == 'contact_info':
            form = EmployerContactInfoForm(request.POST, instance=profile, user=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Contact information updated successfully!')
                return redirect('dashboard:employer_settings')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif form_type == 'business_permit':
            form = EmployerBusinessPermitForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Business permit updated successfully!')
                return redirect('dashboard:employer_settings')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif form_type == 'social_links_bulk':
            try:
                platforms = request.POST.getlist('platform[]')
                urls = request.POST.getlist('url[]')
                link_ids = request.POST.getlist('link_id[]')
                
                existing_ids = set(request.user.social_links.values_list('id', flat=True))
                submitted_ids = set()
                
                for i, (platform, url) in enumerate(zip(platforms, urls)):
                    if not platform or not url:
                        continue
                    
                    link_id = link_ids[i] if i < len(link_ids) and link_ids[i] else None
                    
                    if link_id:
                        link_id = int(link_id)
                        submitted_ids.add(link_id)
                        social_link = UserSocialLink.objects.filter(id=link_id, user=request.user).first()
                        if social_link:
                            social_link.platform = platform
                            social_link.url = url
                            social_link.save()
                    else:
                        social_link = UserSocialLink.objects.create(
                            user=request.user,
                            platform=platform,
                            url=url
                        )
                        submitted_ids.add(social_link.id)
                
                ids_to_delete = existing_ids - submitted_ids
                if ids_to_delete:
                    UserSocialLink.objects.filter(id__in=ids_to_delete, user=request.user).delete()
                
                messages.success(request, 'Social links updated successfully!')
                return redirect('dashboard:employer_settings')
            except Exception as e:
                messages.error(request, f'Error updating social links: {str(e)}')
        
        elif form_type == 'social_link':
            social_link_id = request.POST.get('social_link_id')
            if social_link_id:
                social_link = get_object_or_404(UserSocialLink, id=social_link_id, user=request.user)
                form = ApplicantSocialLinkForm(request.POST, instance=social_link)
            else:
                form = ApplicantSocialLinkForm(request.POST)
            
            if form.is_valid():
                social_link = form.save(commit=False)
                social_link.user = request.user
                social_link.save()
                messages.success(request, 'Social link saved successfully!')
                return redirect('dashboard:employer_settings')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif form_type == 'delete_social_link':
            social_link_id = request.POST.get('social_link_id')
            social_link = get_object_or_404(UserSocialLink, id=social_link_id, user=request.user)
            social_link.delete()
            messages.success(request, 'Social link deleted successfully!')
            return redirect('dashboard:employer_settings')
        
        elif form_type == 'change_password':
            form = PasswordChangeForm(user=request.user, data=request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully!')
                return redirect('dashboard:employer_settings')
            else:
                for error in form.errors.values():
                    messages.error(request, error[0])
        
        return self.get(request, *args, **kwargs)


class ApplicantSettingsView(ApplicantRequiredMixin, TemplateView):
    """
    Applicant settings page handling multiple forms:
    - Personal info, profile details, contact info, privacy
    - Resume upload, password change, notification preferences
    - Social links management, account deletion
    Matches the logic of the original applicant_settings function-based view.
    """
    template_name = 'dashboard/applicant/applicant_settings.html'
    
    def get_context_data(self, **kwargs):
        from applicant_profile.models import NotificationPreferences
        
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(ApplicantProfile, user=self.request.user)
        
        # Get or create notification preferences
        notification_prefs, created = NotificationPreferences.objects.get_or_create(
            user=self.request.user,
            defaults={
                'notify_shortlisted': True,
                'notify_applications': True,
                'notify_job_alerts': True
            }
        )
        
        # Initialize all forms with current data
        context['profile'] = profile
        context['personal_info_form'] = ApplicantPersonalInfoForm(instance=profile)
        context['profile_details_form'] = ApplicantProfileDetailsForm(instance=profile)
        context['contact_info_form'] = ApplicantContactInfoForm(instance=profile, user=self.request.user)
        context['profile_privacy_form'] = ApplicantProfilePrivacyForm(instance=profile)
        context['resume_form'] = ApplicantResumeForm(instance=profile)
        context['password_form'] = PasswordChangeForm(self.request.user)
        context['social_link_form'] = ApplicantSocialLinkForm()
        context['social_links'] = self.request.user.social_links.all()
        context['notification_prefs'] = notification_prefs
        
        return context
    
    def post(self, request, *args, **kwargs):
        from applicant_profile.models import NotificationPreferences
        from django.contrib.auth import authenticate
        
        profile = get_object_or_404(ApplicantProfile, user=request.user)
        notification_prefs, _ = NotificationPreferences.objects.get_or_create(
            user=request.user,
            defaults={
                'notify_shortlisted': True,
                'notify_applications': True,
                'notify_job_alerts': True
            }
        )
        
        form_type = request.POST.get('form_type')
        
        if form_type == 'personal_info':
            form = ApplicantPersonalInfoForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Personal information updated successfully!')
                    return redirect('dashboard:applicant_settings')
                except Exception as e:
                    messages.error(request, f'Error saving personal information: {str(e)}')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
                messages.error(request, 'Please correct the errors below.')
        
        elif form_type == 'profile_details':
            form = ApplicantProfileDetailsForm(request.POST, instance=profile)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Profile details updated successfully!')
                    return redirect('dashboard:applicant_settings')
                except Exception as e:
                    messages.error(request, f'Error saving profile details: {str(e)}')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
                messages.error(request, 'Please correct the errors below.')
        
        elif form_type == 'social_links_bulk':
            try:
                # Get arrays from POST data
                platforms = request.POST.getlist('platform[]')
                urls = request.POST.getlist('url[]')
                link_ids = request.POST.getlist('link_id[]')
                
                # Get existing social link IDs for this user
                existing_ids = set(request.user.social_links.values_list('id', flat=True))
                submitted_ids = set()
                
                # Process each submitted link
                for i, (platform, url) in enumerate(zip(platforms, urls)):
                    if not platform or not url:
                        continue
                    
                    link_id = link_ids[i] if i < len(link_ids) and link_ids[i] else None
                    
                    if link_id:
                        # Update existing link
                        link_id = int(link_id)
                        submitted_ids.add(link_id)
                        social_link = UserSocialLink.objects.filter(id=link_id, user=request.user).first()
                        if social_link:
                            social_link.platform = platform
                            social_link.url = url
                            social_link.save()
                    else:
                        # Create new link
                        social_link = UserSocialLink.objects.create(
                            user=request.user,
                            platform=platform,
                            url=url
                        )
                        submitted_ids.add(social_link.id)
                
                # Delete links that were removed (in existing but not in submitted)
                ids_to_delete = existing_ids - submitted_ids
                if ids_to_delete:
                    UserSocialLink.objects.filter(id__in=ids_to_delete, user=request.user).delete()
                
                messages.success(request, 'Social links updated successfully!')
                return redirect('dashboard:applicant_settings')
            except Exception as e:
                messages.error(request, f'Error updating social links: {str(e)}')
        
        elif form_type == 'social_link':
            social_link_id = request.POST.get('social_link_id')
            if social_link_id:
                # Edit existing social link
                social_link = get_object_or_404(UserSocialLink, id=social_link_id, user=request.user)
                form = ApplicantSocialLinkForm(request.POST, instance=social_link)
            else:
                # Add new social link
                form = ApplicantSocialLinkForm(request.POST)
            
            if form.is_valid():
                social_link = form.save(commit=False)
                social_link.user = request.user
                social_link.save()
                messages.success(request, 'Social link saved successfully!')
                return redirect('dashboard:applicant_settings')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif form_type == 'delete_social_link':
            social_link_id = request.POST.get('social_link_id')
            social_link = get_object_or_404(UserSocialLink, id=social_link_id, user=request.user)
            social_link.delete()
            messages.success(request, 'Social link deleted successfully!')
            return redirect('dashboard:applicant_settings')
        
        elif form_type == 'contact_info':
            form = ApplicantContactInfoForm(request.POST, instance=profile, user=request.user)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Contact information updated successfully!')
                    return redirect('dashboard:applicant_settings')
                except Exception as e:
                    messages.error(request, f'Error saving contact information: {str(e)}')
            else:
                for field, errors in form.errors.items():
                    field_label = form.fields.get(field).label if field in form.fields else field
                    for error in errors:
                        messages.error(request, f'{field_label}: {error}')
        
        elif form_type == 'profile_privacy':
            form = ApplicantProfilePrivacyForm(request.POST, instance=profile)
            if form.is_valid():
                try:
                    form.save()
                    status = 'public' if form.cleaned_data['is_public'] else 'private'
                    messages.success(request, f'Profile privacy set to {status}!')
                    return redirect('dashboard:applicant_settings')
                except Exception as e:
                    messages.error(request, f'Error saving privacy settings: {str(e)}')
            else:
                for field, errors in form.errors.items():
                    field_label = form.fields.get(field).label if field in form.fields else field
                    for error in errors:
                        messages.error(request, f'{field_label}: {error}')
        
        elif form_type == 'resume':
            form = ApplicantResumeForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'Resume uploaded successfully!')
                    return redirect('dashboard:applicant_settings')
                except Exception as e:
                    messages.error(request, f'Error uploading resume: {str(e)}')
            else:
                for field, errors in form.errors.items():
                    field_label = form.fields.get(field).label if field in form.fields else field
                    for error in errors:
                        messages.error(request, f'{field_label}: {error}')
        
        elif form_type == 'change_password':
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                try:
                    user = password_form.save()
                    update_session_auth_hash(request, user)  # Keep user logged in
                    messages.success(request, 'Password changed successfully!')
                    return redirect('dashboard:applicant_settings')
                except Exception as e:
                    messages.error(request, f'Error changing password: {str(e)}')
            else:
                # Display password form errors with field labels
                for field, errors in password_form.errors.items():
                    field_label = password_form.fields.get(field).label if field in password_form.fields else field
                    for error in errors:
                        messages.error(request, f'{field_label}: {error}')
        
        elif form_type == 'notification_preferences':
            # Update notification preferences
            notification_prefs.notify_shortlisted = request.POST.get('notify_shortlisted') == 'on'
            notification_prefs.notify_applications = request.POST.get('notify_applications') == 'on'
            notification_prefs.notify_job_alerts = request.POST.get('notify_job_alerts') == 'on'
            notification_prefs.save()
            messages.success(request, 'Notification preferences updated successfully!')
            return redirect('dashboard:applicant_settings')
        
        elif form_type == 'delete_account':
            # Verify password
            password = request.POST.get('password')
            user = authenticate(username=request.user.username, password=password)
            
            if user is not None:
                try:
                    # Delete user account (cascades to profile and related data)
                    username = request.user.username
                    request.user.delete()
                    messages.success(request, f'Account {username} has been permanently deleted.')
                    return redirect('home')
                except Exception as e:
                    messages.error(request, f'Error deleting account: {str(e)}')
            else:
                messages.error(request, 'Incorrect password. Account deletion cancelled.')
                return redirect('dashboard:applicant_settings')
        
        # Return context with all forms if no redirect happened
        return self.get(request, *args, **kwargs)


class EmployerProfileView(EmployerRequiredMixin, TemplateView):
    """
    Display employer profile with company information and statistics.
    Matches the logic of the original employer_profile function-based view.
    """
    template_name = 'dashboard/employer/employer_profile.html'
    
    def get_context_data(self, **kwargs):
        from jobs.models import Job, JobApplication
        from django.db.models import Count
        
        context = super().get_context_data(**kwargs)
        
        # Get employer profile
        try:
            profile = self.request.user.employer_profile_rel
        except:
            profile = None
        
        # Get social links
        social_links = UserSocialLink.objects.filter(user=self.request.user).order_by('platform')
        
        # Get recent jobs with application counts and related data
        recent_jobs = Job.objects.filter(
            employer=self.request.user
        ).select_related(
            'category',
            'job_type',
            'education',
            'experience',
            'job_level',
            'salary_type'
        ).annotate(
            applications_count=Count('applications')
        ).order_by('-posted_at')[:3]
        
        # Calculate statistics (optimized single query for total applications)
        total_jobs = Job.objects.filter(employer=self.request.user).count()
        active_jobs = Job.objects.filter(employer=self.request.user, status='active').count()
        
        # Single query for total applications instead of looping
        total_applications = JobApplication.objects.filter(job__employer=self.request.user).count()
        hired_count = JobApplication.objects.filter(job__employer=self.request.user, status='hired').count()
        
        context.update({
            'profile': profile,
            'social_links': social_links,
            'recent_jobs': recent_jobs,
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'total_applications': total_applications,
            'hired_count': hired_count,
            'is_owner': True,
        })
        
        return context
