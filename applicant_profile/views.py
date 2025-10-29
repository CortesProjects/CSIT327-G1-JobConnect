from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import ApplicantProfile
from .forms import PersonalInfoForm, EducationForm, SkillsResumeForm

@login_required
def applicant_profile_setup_step1(request):
    profile, created = ApplicantProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = PersonalInfoForm(request.POST, instance=profile)
        if form.is_valid():
            saved_profile = form.save()
            # Update progress to allow access to step 2
            if saved_profile.setup_step_progress < 2:
                saved_profile.setup_step_progress = 2
                saved_profile.save()
            return redirect('applicant_profile:applicant_profile_setup_step2')
    else:
        form = PersonalInfoForm(instance=profile)
    
    context = {
        'form': form,
        'is_setup_page': True, # Tells base.html to show the bar
        'progress_percent': 0,
        'progress': profile.setup_step_progress # Get value from the model property
    }
    return render(request, 'applicant_profile/applicant_profile_step1.html', context)

@login_required
def applicant_profile_setup_step2(request):
    profile = request.user.applicant_profile_rel
    
    # SECURITY CHECK: Redirect if user hasn't completed step 1
    if profile.setup_step_progress < 2:
        return redirect('applicant_profile:applicant_profile_setup_step1')

    if request.method == 'POST':
        form = EducationForm(request.POST, instance=profile)
        if form.is_valid():
            saved_profile = form.save()
            # Update progress to allow access to step 3
            if saved_profile.setup_step_progress < 3:
                saved_profile.setup_step_progress = 3
                saved_profile.save()
            return redirect('applicant_profile:applicant_profile_setup_step3')
    else:
        form = EducationForm(instance=profile)
    
    context = {
        'form': form,
        'is_setup_page': True, # Tells base.html to show the bar
        'progress_percent':33,
        'progress': profile.setup_step_progress
    }
    return render(request, 'applicant_profile/applicant_profile_step2.html', context)

@login_required
def applicant_profile_setup_step3(request):
    profile = request.user.applicant_profile_rel

    # SECURITY CHECK: Redirect if user hasn't completed step 2
    if profile.setup_step_progress < 3:
        return redirect('applicant_profile:applicant_profile_setup_step2')

    if request.method == 'POST':
        form = SkillsResumeForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            profile.calculate_completeness()
            return redirect('applicant_profile:applicant_profile_setup_complete')
    else:
        form = SkillsResumeForm(instance=profile)
        
    context = {
        'form': form,
        'is_setup_page': True, 
        'progress_percent': 66,
        'progress': profile.setup_step_progress
    }
    return render(request, 'applicant_profile/applicant_profile_step3.html', context)

@login_required
def applicant_profile_setup_complete(request):
    """Displays the final completion page."""
    context = {
        'is_setup_page': True,
        'progress_percent': 100
    }
    return render(request, 'applicant_profile/applicant_profile_completion.html',context)