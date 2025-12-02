from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from applicant_profile.models import ApplicantProfile
from resumes.models import Resume
from utils.mixins import applicant_required
from .forms import PersonalInfoForm, ProfileDetailsForm, ContactInfoForm, ResumeUploadSetupForm

@applicant_required
def applicant_profile_setup_step1(request):
    profile, created = ApplicantProfile.objects.get_or_create(user=request.user)
    
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
    
    # Previously enforced server-side progress gating; frontend now handles step access

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

    # Previously enforced server-side progress gating; frontend now handles step access

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
    context = {
        'is_setup_page': True,
        'progress_percent': 100
    }
    return render(request, 'applicant_profile/applicant_profile_completion.html',context)