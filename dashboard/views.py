# dashboards/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from accounts.models import User, ApplicantProfile, ApplicantSocialLink
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
        # The main dashboard view now renders the overview template.
        return render(request, 'dashboard/applicant/applicant_overview.html')
    elif user.user_type == 'employer':
        return render(request, 'dashboard/employer/employer_overview.html')
    elif user.user_type == 'admin':
        return render(request, 'dashboard/admin/admin_dashboards.html')
    else:
        # Fallback for any other user type or if user_type is not set
        return render(request, 'home.html')

@login_required
def applicant_applied_jobs(request):
    context = {} # Add any context needed for the template
    return render(request, 'dashboard/applicant/applicant_applied_jobs.html', context)

@login_required
def applicant_favorite_jobs(request):
    context = {} # Add any context needed for the template
    return render(request, 'dashboard/applicant/applicant_favorite_jobs.html', context)

@login_required
def applicant_job_alerts(request):
    context = {} # Add any context needed for the template
    return render(request, 'dashboard/applicant/applicant_job_alerts.html', context)

@login_required
def applicant_settings(request):
    profile = get_object_or_404(ApplicantProfile, user=request.user)
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'personal_info':
            form = ApplicantPersonalInfoForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Personal information updated successfully!')
                return redirect('dashboard:applicant_settings')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif form_type == 'profile_details':
            form = ApplicantProfileDetailsForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile details updated successfully!')
                return redirect('dashboard:applicant_settings')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif form_type == 'social_link':
            social_link_id = request.POST.get('social_link_id')
            if social_link_id:
                # Edit existing social link
                social_link = get_object_or_404(ApplicantSocialLink, id=social_link_id, profile=profile)
                form = ApplicantSocialLinkForm(request.POST, instance=social_link)
            else:
                # Add new social link
                form = ApplicantSocialLinkForm(request.POST)
            
            if form.is_valid():
                social_link = form.save(commit=False)
                social_link.profile = profile
                social_link.save()
                messages.success(request, 'Social link saved successfully!')
                return redirect('dashboard:applicant_settings')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif form_type == 'delete_social_link':
            social_link_id = request.POST.get('social_link_id')
            social_link = get_object_or_404(ApplicantSocialLink, id=social_link_id, profile=profile)
            social_link.delete()
            messages.success(request, 'Social link deleted successfully!')
            return redirect('dashboard:applicant_settings')
        
        elif form_type == 'contact_info':
            form = ApplicantContactInfoForm(request.POST, instance=profile, user=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Contact information updated successfully!')
                return redirect('dashboard:applicant_settings')
            else:
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
                profile.calculate_completeness()
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
    
    # Get existing social links
    social_links = profile.social_links.all()
    
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
    return render(request, 'dashboard/employer/employer_post_job.html')

@login_required
def employer_my_jobs(request):
    return render(request, 'dashboard/employer/employer_my_jobs.html')

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
def employer_job_applications(request):
    return render(request, 'dashboard/employer/employer_job_applications.html')

@login_required
def employer_candidate_detail(request):
    return render(request, 'dashboard/employer/employer_candidate_detail.html')

#------------------------------------------
#              Admin Stuff
#------------------------------------------
@login_required
def admin_dashboards(request):
    total_verified_employers = User.objects.filter(user_type='employer', is_verified=True).count()
    total_unverified_employers = User.objects.filter(user_type='employer', is_verified=False).count()
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
    verified_employers = User.objects.filter(user_type='employer', is_verified=True).select_related('employer_profile_rel')

    context = {
        'verified_employers': verified_employers,
    }
    return render(request, "dashboard/admin/admin_total_employers_verified.html", context)

@login_required
def admin_accept_reject_employer(request):
    unverified_employers = User.objects.filter(user_type='employer', is_verified=False)

    context = {
        'unverified_employers': unverified_employers
    }
    return render(request, 'dashboard/admin/admin_accept_reject_employer.html', context)

@login_required
@user_passes_test(lambda u: u.user_type == 'admin')  # Only admins can approve
def approve_employer(request, employer_id):
    if request.method == 'POST':
        employer = get_object_or_404(User, id=employer_id, user_type='employer')
        employer.is_verified = True
        employer.save()
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