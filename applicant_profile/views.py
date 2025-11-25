from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from applicant_profile.models import ApplicantProfile
from .forms import PersonalInfoForm, ProfileDetailsForm, ContactInfoForm

@login_required
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

@login_required
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
        'progress_percent':33,
    }
    return render(request, 'applicant_profile/applicant_profile_step2.html', context)

@login_required
def applicant_profile_setup_step3(request):
    profile = request.user.applicant_profile_rel

    # Previously enforced server-side progress gating; frontend now handles step access

    if request.method == 'POST':
        form = ContactInfoForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('applicant_profile:applicant_profile_setup_complete')
    else:
        form = ContactInfoForm(instance=profile)
        
    context = {
        'form': form,
        'is_setup_page': True, 
        'progress_percent': 66,
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