from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from employer_profile.models import EmployerProfile 
from .forms import (
    EmployerProfileCompanyInfoForm, 
    EmployerProfileFoundingInfoForm, 
    EmployerProfileContactForm
)

@login_required
# @check_employer_access (Assuming you apply this decorator)
def employer_profile_setup_step1(request):
    # redirect_check = check_employer_access(request.user)
    # if redirect_check: return redirect_check
    
    profile, created = EmployerProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = EmployerProfileCompanyInfoForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            form.save()
            return redirect('employer_profile:employer_profile_setup_step2')
        else:
            messages.error(request, "Please correct the errors, including file format/size.")
    else:
        form = EmployerProfileCompanyInfoForm(instance=profile)

    context = {
        'form': form,
        'is_setup_page': True,
        'step_title': "Company Info",
        'progress_percent': 0,
    }
    return render(request, 'employer_profile/employer_profile_step1.html', context)

@login_required
def employer_profile_setup_step2(request):
    # redirect_check = check_employer_access(request.user)
    # if redirect_check: return redirect_check

    profile = get_object_or_404(EmployerProfile, user=request.user)
    
    if request.method == 'POST':
        form = EmployerProfileFoundingInfoForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('employer_profile:employer_profile_setup_step3')
        else:
            messages.error(request, "Please correct the errors.")
    else:
        form = EmployerProfileFoundingInfoForm(instance=profile)
        
    context = {
        'form': form,
        'step_title': "Founding Info",
        'is_setup_page': True, 
        'progress_percent':33,
    }
    return render(request, 'employer_profile/employer_profile_step2.html', context)

@login_required
def employer_profile_setup_step3(request):
    # redirect_check = check_employer_access(request.user)
    # if redirect_check: return redirect_check

    profile = get_object_or_404(EmployerProfile, user=request.user)
    
    if request.method == 'POST':
        form = EmployerProfileContactForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Contact Info saved. Profile is complete!")
            return redirect('employer_profile:employer_profile_completion')
        else:
            messages.error(request, "Please correct the errors.")
    else:
        form = EmployerProfileContactForm(instance=profile)
        
    context = {
        'form': form,
        'step_title': "Contact",
        'is_setup_page': True, 
        'progress_percent': 66,
    }
    return render(request, 'employer_profile/employer_profile_step3.html', context)


@login_required
def employer_profile_completion(request):
    context = {
        'is_setup_page': True,
        'progress_percent': 100
    }
    return render(request, 'employer_profile/employer_profile_completion.html', context)
