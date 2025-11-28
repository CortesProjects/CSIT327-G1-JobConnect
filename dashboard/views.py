# dashboards/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone
from accounts.models import User, UserSocialLink, UserVerification
from applicant_profile.models import ApplicantProfile
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

@login_required
def dashboard_view(request):
    user = request.user
    if user.user_type == 'applicant':
        return render(request, 'dashboard/applicant/applicant_overview.html')
    elif user.user_type == 'employer':
        from jobs.models import Job
        from django.db.models import Count
        
        # Fetch employer's jobs with application counts
        all_jobs = Job.objects.filter(employer=request.user)
        recent_jobs = all_jobs.annotate(
            applications_count=Count('applications')
        ).order_by('-posted_at')[:5]
        
        context = {
            'has_jobs': all_jobs.exists(),
            'open_jobs_count': all_jobs.filter(status='active').count(),
            'total_jobs_count': all_jobs.count(),
            'recent_jobs': recent_jobs,
            'saved_candidates_count': 0,  # TODO: Implement when application system is ready
        }
        
        return render(request, 'dashboard/employer/employer_overview.html', context)
    elif user.user_type == 'admin':
        return render(request, 'dashboard/admin/admin_dashboards.html')
    else:
        return render(request, 'home.html')

@login_required
def applicant_search_jobs(request):
    """Search jobs for applicants with filters using Django form validation"""
    from jobs.models import (
        Job, JobCategory, EducationLevel, 
        ExperienceLevel, JobLevel, FavoriteJob
    )
    from django.db.models import Q, Count
    from dashboard.forms import JobSearchForm
    
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
    form = JobSearchForm(
        request.GET or None,
        category_choices=category_choices,
        education_choices=education_choices,
        experience_choices=experience_choices,
        job_level_choices=job_level_choices
    )
    
    # Start with active jobs only
    jobs = Job.objects.filter(status='active').annotate(applications_count=Count('applications'))
    
    # Apply filters only if form is valid
    if form.is_valid():
        cleaned_data = form.cleaned_data
        
        # Keyword search
        query = cleaned_data.get('query')
        if query:
            # Search title, description, company name, legacy tags field, and related Tag names
            jobs = jobs.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(company_name__icontains=query) |
                Q(tags__icontains=query) |
                Q(job_tags__tag__name__icontains=query)
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
    jobs = jobs.order_by('-posted_at')
    
    # Get favorited job IDs for the current applicant
    favorited_job_ids = []
    if request.user.is_authenticated and request.user.user_type == 'applicant':
        favorited_job_ids = list(
            FavoriteJob.objects.filter(applicant=request.user).values_list('job_id', flat=True)
        )
    
    context = {
        "form": form,
        "jobs": jobs,
        "categories": all_categories,
        "educations": all_educations,
        "experiences": all_experiences,
        "job_levels": all_job_levels,
        "favorited_job_ids": favorited_job_ids,
    }
    
    return render(request, 'dashboard/applicant/applicant_search_jobs.html', context)

@login_required
def applicant_applied_jobs(request):
    context = {}
    return render(request, 'dashboard/applicant/applicant_applied_jobs.html', context)

@login_required
def applicant_favorite_jobs(request):
    from jobs.models import FavoriteJob
    
    if request.user.user_type != 'applicant':
        messages.error(request, 'Only applicants can view favorite jobs.')
        return redirect('dashboard')
    
    # Get all favorite jobs with related data
    favorites = FavoriteJob.objects.filter(
        applicant=request.user
    ).select_related(
        'job',
        'job__employer',
        'job__category',
        'job__job_type',
        'job__education',
        'job__experience',
        'job__job_level'
    ).order_by('-created_at')
    
    # Get list of favorited job IDs (all jobs in favorites by definition)
    favorited_job_ids = list(favorites.values_list('job_id', flat=True))
    
    context = {
        'favorites': favorites,
        'favorite_count': favorites.count(),
        'favorited_job_ids': favorited_job_ids,
    } 
    return render(request, 'dashboard/applicant/applicant_favorite_jobs.html', context)

@login_required
def applicant_job_alerts(request):
    from jobs.models import FavoriteJob
    
    # Get favorited job IDs for bookmark state
    favorited_job_ids = []
    if request.user.is_authenticated and request.user.user_type == 'applicant':
        favorited_job_ids = list(
            FavoriteJob.objects.filter(applicant=request.user).values_list('job_id', flat=True)
        )
    
    context = {
        'favorited_job_ids': favorited_job_ids,
    } 
    return render(request, 'dashboard/applicant/applicant_job_alerts.html', context)

@login_required
def applicant_settings(request):
    profile = get_object_or_404(ApplicantProfile, user=request.user)
    
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
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
                messages.error(request, 'Please correct the errors below.')
        
        elif form_type == 'profile_privacy':
            form = ApplicantProfilePrivacyForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                status = 'public' if form.cleaned_data['is_public'] else 'private'
                messages.success(request, f'Profile privacy set to {status}!')
                return redirect('dashboard:applicant_settings')
        
        elif form_type == 'resume':
            form = ApplicantResumeForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Resume uploaded successfully!')
                return redirect('dashboard:applicant_settings')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif form_type == 'change_password':
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Keep user logged in
                messages.success(request, 'Password changed successfully!')
                return redirect('dashboard:applicant_settings')
            else:
                messages.error(request, 'Please correct the errors in the password form.')
    
    # Initialize all forms with current data
    personal_info_form = ApplicantPersonalInfoForm(instance=profile)
    profile_details_form = ApplicantProfileDetailsForm(instance=profile)
    contact_info_form = ApplicantContactInfoForm(instance=profile, user=request.user)
    profile_privacy_form = ApplicantProfilePrivacyForm(instance=profile)
    resume_form = ApplicantResumeForm(instance=profile)
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
    }
    
    return render(request, 'dashboard/applicant/applicant_settings.html', context)

@login_required
def employer_profile(request):
    return render(request, 'dashboard/employer/employer_profile.html')

@login_required
def employer_post_job(request):
    """Handle job posting creation"""
    # Ensure user is an employer
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. Employer account required.')
        return redirect('accounts:login')
    
    # Get employer profile for company name
    try:
        employer_profile = request.user.employer_profile_rel
        if not employer_profile.company_name:
            messages.warning(request, 'Please complete your company profile before posting a job.')
            return redirect('dashboard:employer_settings')
    except:
        messages.error(request, 'Please complete your profile setup first.')
        return redirect('dashboard:employer_settings')
    
    if request.method == 'POST':
        from jobs.forms import JobPostForm
        form = JobPostForm(request.POST)

        if form.is_valid():
            try:
                job = form.save(commit=False)
                job.employer = request.user
                job.company_name = employer_profile.company_name
                job.status = 'active'
                job.save()

                # messages.success(request, 'Job posted successfully!')
                return redirect(f"{reverse('dashboard:employer_post_job')}?success=true")
            except Exception as e:
                messages.error(request, f'Error posting job: {str(e)}')
        else:
            # Do not push per-field errors to messages container; render form with inline errors
            pass
        # end POST

    else:
        # GET - instantiate empty form
        from jobs.forms import JobPostForm
        form = JobPostForm()

    return render(request, 'dashboard/employer/employer_post_job.html', {
        'company_name': employer_profile.company_name if employer_profile else '',
        'form': form,
    })

@login_required
def employer_my_jobs(request):
    """Display all jobs posted by the employer with filtering"""
    # Validate user is employer
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. Employer account required.')
        return redirect('dashboard:dashboard')
    
    from jobs.models import Job
    
    # Fetch jobs posted by this employer
    all_jobs = Job.objects.filter(employer=request.user).order_by('-posted_at')
    
    # Apply status filter
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        all_jobs = all_jobs.filter(status=status_filter)
    
    context = {
        'all_jobs': all_jobs,
        'has_jobs': all_jobs.exists(),
        'total_jobs': all_jobs.count(),
        'status_filter': status_filter,
    }
    
    return render(request, 'dashboard/employer/employer_my_jobs.html', context)


@login_required
def employer_settings(request):
    """Handle employer settings with multiple form types"""
    try:
        profile = request.user.employer_profile_rel
    except:
        messages.error(request, "Employer profile not found.")
        return redirect('dashboard:employer_dashboard')
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        # Company Info Form
        if form_type == 'company_info':
            form = EmployerCompanyInfoForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Company information updated successfully!')
                return redirect('dashboard:employer_settings')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        # Founding Info Form
        elif form_type == 'founding_info':
            form = EmployerFoundingInfoForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Founding information updated successfully!')
                return redirect('dashboard:employer_settings')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        # Contact Info Form
        elif form_type == 'contact_info':
            form = EmployerContactInfoForm(request.POST, instance=profile, user=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Contact information updated successfully!')
                return redirect('dashboard:employer_settings')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        # Business Permit Form
        elif form_type == 'business_permit':
            form = EmployerBusinessPermitForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Business permit uploaded successfully!')
                return redirect('dashboard:employer_settings')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        # Change Password Form
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
    
    # Initialize all forms with current data
    company_info_form = EmployerCompanyInfoForm(instance=profile)
    founding_info_form = EmployerFoundingInfoForm(instance=profile)
    contact_info_form = EmployerContactInfoForm(instance=profile, user=request.user)
    business_permit_form = EmployerBusinessPermitForm(instance=profile)
    password_form = PasswordChangeForm(user=request.user)
    
    context = {
        'profile': profile,
        'company_info_form': company_info_form,
        'founding_info_form': founding_info_form,
        'contact_info_form': contact_info_form,
        'business_permit_form': business_permit_form,
        'password_form': password_form,
    }
    
    return render(request, 'dashboard/employer/employer_settings.html', context)

@login_required
def employer_job_applications(request, job_id):
    """Show applications for a specific job posting (employer-only)."""
    from django.shortcuts import get_object_or_404
    from django.core.exceptions import PermissionDenied
    from jobs.models import Job

    # Ensure user is an employer
    if getattr(request.user, 'user_type', None) != 'employer':
        messages.error(request, 'Access denied. Employer account required.')
        return redirect('dashboard:dashboard')

    # Ensure the job exists and belongs to the current employer
    job = get_object_or_404(Job, id=job_id)
    if job.employer_id != request.user.id:
        raise PermissionDenied("You do not have permission to view these applications.")

    # Get all applications for this job
    applications_qs = []
    if hasattr(job, 'applications'):
        try:
            applications_qs = job.applications.all()
        except Exception:
            applications_qs = []
    elif hasattr(job, 'application_set'):
        try:
            applications_qs = job.application_set.all()
        except Exception:
            applications_qs = []

    # TODO: When ApplicationStage model exists, fetch custom stages for this job
    # For now, using empty list - columns will be created by employer
    custom_columns = []
    # Example structure when implemented:
    # custom_columns = ApplicationStage.objects.filter(job=job).prefetch_related('applications')
    # Each column should have: id, name, applications (queryset)

    context = {
        'job': job,
        'all_applications': applications_qs,  # All applications in first column
        'custom_columns': custom_columns,      # Dynamic stages (Shortlisted, Interview, etc.)
    }
    return render(request, 'dashboard/employer/employer_job_applications.html', context)

@login_required
def employer_candidate_detail(request):
    return render(request, 'dashboard/employer/employer_candidate_detail.html')

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
    # total_job_postings = JobPosting.objects.filter(is_active=True).count()

    context = {
        'total_verified_employers': total_verified_employers,
        'total_unverified_employers': total_unverified_employers,
        'total_applicants': total_applicants,
        # 'total_job_postings': total_job_postings,
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
@user_passes_test(lambda u: u.user_type == 'admin')  # Only admins can approve
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
@user_passes_test(lambda u: u.user_type == 'admin')  # Only admins can reject
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
def admin_job_postings(request):

    return render(request, "dashboard/admin/admin_job_postings.html")
#------------------------------------------
#          Admin Stuff Ends Here
# -----------------------------------------