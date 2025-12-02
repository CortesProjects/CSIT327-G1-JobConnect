from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from applicant_profile.models import ApplicantProfile
from resumes.models import Resume
from utils.mixins import applicant_required
from .forms import PersonalInfoForm, ProfileDetailsForm, ContactInfoForm, ResumeUploadSetupForm


def is_step1_complete(profile):
    """Check if Step 1 (Personal Info) is complete."""
    return bool(
        profile.first_name and 
        profile.last_name and 
        profile.education_level and
        profile.experience
    )


def is_step2_complete(profile):
    """Check if Step 2 (Profile Details) is complete."""
    return bool(profile.date_of_birth)


def is_step3_complete(profile):
    """Check if Step 3 (Contact Info) is complete."""
    return bool(profile.contact_number)

@applicant_required
def applicant_profile_setup_step1(request):
    profile, created = ApplicantProfile.objects.get_or_create(user=request.user)
    
    # Redirect if setup already completed
    if profile.setup_completed:
        messages.info(request, 'You have already completed your profile setup.')
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = PersonalInfoForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('applicant_profile:applicant_profile_setup_step2')
    else:
        form = PersonalInfoForm(instance=profile)
    
    context = {
        'form': form,
        'is_setup_page': True, # Tells base.html to show the bar
        'progress_percent': 0,
    }
    return render(request, 'applicant_profile/applicant_profile_step1.html', context)

@applicant_required
def applicant_profile_setup_step2(request):
    profile = request.user.applicant_profile_rel
    
    # Redirect if setup already completed
    if profile.setup_completed:
        messages.info(request, 'You have already completed your profile setup.')
        return redirect('dashboard:dashboard')
    
    # Validate that step 1 is complete before allowing access to step 2
    if not is_step1_complete(profile):
        messages.warning(request, 'Please complete Step 1 (Personal Information) before proceeding to Step 2.')
        return redirect('applicant_profile:applicant_profile_setup_step1')

    if request.method == 'POST':
        form = ProfileDetailsForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('applicant_profile:applicant_profile_setup_step3')
    else:
        form = ProfileDetailsForm(instance=profile)
    
    context = {
        'form': form,
        'is_setup_page': True, # Tells base.html to show the bar
        'progress_percent':25,
    }
    return render(request, 'applicant_profile/applicant_profile_step2.html', context)

@applicant_required
def applicant_profile_setup_step3(request):
    profile = request.user.applicant_profile_rel
    
    # Redirect if setup already completed
    if profile.setup_completed:
        messages.info(request, 'You have already completed your profile setup.')
        return redirect('dashboard:dashboard')

    # Validate that steps 1 and 2 are complete before allowing access to step 3
    if not is_step1_complete(profile):
        messages.warning(request, 'Please complete Step 1 (Personal Information) before proceeding.')
        return redirect('applicant_profile:applicant_profile_setup_step1')
    
    if not is_step2_complete(profile):
        messages.warning(request, 'Please complete Step 2 (Profile Details) before proceeding to Step 3.')
        return redirect('applicant_profile:applicant_profile_setup_step2')

    if request.method == 'POST':
        form = ContactInfoForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('applicant_profile:applicant_profile_setup_step4')
    else:
        form = ContactInfoForm(instance=profile)
        
    context = {
        'form': form,
        'is_setup_page': True, 
        'progress_percent': 50,
    }
    return render(request, 'applicant_profile/applicant_profile_step3.html', context)

@applicant_required
def applicant_profile_setup_step4(request):
    """Step 4: Resume upload (required) using new Resume model."""
    profile = request.user.applicant_profile_rel
    
    # Redirect if setup already completed
    if profile.setup_completed:
        messages.info(request, 'You have already completed your profile setup.')
        return redirect('dashboard:dashboard')
    
    # Validate that steps 1, 2, and 3 are complete before allowing access to step 4
    if not is_step1_complete(profile):
        messages.warning(request, 'Please complete Step 1 (Personal Information) before proceeding.')
        return redirect('applicant_profile:applicant_profile_setup_step1')
    
    if not is_step2_complete(profile):
        messages.warning(request, 'Please complete Step 2 (Profile Details) before proceeding.')
        return redirect('applicant_profile:applicant_profile_setup_step2')
    
    if not is_step3_complete(profile):
        messages.warning(request, 'Please complete Step 3 (Contact Information) before proceeding to Step 4.')
        return redirect('applicant_profile:applicant_profile_setup_step3')
    
    # Check if user already has at least one resume
    has_resume = Resume.objects.filter(user=request.user).exists()
    
    if request.method == 'POST':
        form = ResumeUploadSetupForm(request.POST, request.FILES)
        if form.is_valid():
            # Create Resume instance
            resume = Resume(
                user=request.user,
                name=form.cleaned_data['resume_name'],
                file=form.cleaned_data['resume_file'],
                is_default=form.cleaned_data.get('set_as_default', True)
            )
            
            # If setting as default, remove default from other resumes
            if resume.is_default:
                Resume.objects.filter(user=request.user, is_default=True).update(is_default=False)
            
            resume.save()
            
            # Mark profile setup as completed
            profile.setup_completed = True
            profile.save()
            
            messages.success(request, f'Resume "{resume.name}" uploaded successfully!')
            return redirect('applicant_profile:applicant_profile_setup_complete')
    else:
        form = ResumeUploadSetupForm()
    
    context = {
        'form': form,
        'has_resume': has_resume,
        'is_setup_page': True,
        'progress_percent': 75,
    }
    return render(request, 'applicant_profile/applicant_profile_step4.html', context)

@applicant_required
def applicant_profile_setup_complete(request):
    """Displays the final completion page."""
    profile = request.user.applicant_profile_rel
    
    # Ensure setup is marked as complete
    if not profile.setup_completed:
        profile.setup_completed = True
        profile.save()
    
    context = {
        'is_setup_page': True,
        'progress_percent': 100
    }
    return render(request, 'applicant_profile/applicant_profile_completion.html',context)