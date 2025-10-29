from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import EmployerProfile 
from .forms import (
    EmployerProfileCompanyInfoForm, 
    EmployerProfileFoundingInfoForm, 
    EmployerProfileContactForm
)

TOTAL_SETUP_STEPS = 3 
STEP_URLS = {
    1: 'employer_profile:employer_profile_setup_step1',
    2: 'employer_profile:employer_profile_setup_step2',
    3: 'employer_profile:employer_profile_setup_step3',
}

def get_setup_context(current_step):
    """Calculates progress and sets up the context for the header."""
    
    percent = int((current_step / TOTAL_SETUP_STEPS) * 100)
    
    return {
        'is_setup_page': True,
        'progress_percent': percent,
        'current_step': current_step,
        'prev_url': STEP_URLS.get(current_step - 1),
    }
# --- Step 1 View: Company Info (URL: employer/profile/company-info/) ---

@login_required
# @check_employer_access (Assuming you apply this decorator)
def employer_profile_setup_step1(request):
    # redirect_check = check_employer_access(request.user)
    # if redirect_check: return redirect_check
    
    profile, created = EmployerProfile.objects.get_or_create(user=request.user)
    current_step = 1
    
    if request.method == 'POST':
        # Handles both text fields and file uploads (request.FILES)
        form = EmployerProfileCompanyInfoForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            profile = form.save(commit=False)
            profile.setup_step = 2
            profile.save()
            # messages.success(request, "Company Info saved. Proceed to Founding Info.")
            return redirect('employer_profile:employer_profile_setup_step2') 
        else:
            messages.error(request, "Please correct the errors, including file format/size.")
    else:
        form = EmployerProfileCompanyInfoForm(instance=profile)
        
    context = {
        'form': form,
        'step_title': "Company Info",
        **get_setup_context(current_step),
    }
    return render(request, 'employer_profile/employer_profile_step1.html', context)

# --- Step 2 View: Founding Info (URL: employer/profile/founding-info/) ---
@login_required
def employer_profile_setup_step2(request):
    # redirect_check = check_employer_access(request.user)
    # if redirect_check: return redirect_check

    profile = get_object_or_404(EmployerProfile, user=request.user)
    current_step = 2
    
    if request.method == 'POST':
        form = EmployerProfileFoundingInfoForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.setup_step = 3
            profile.save()
            # messages.success(request, "Founding Info saved. Proceed to Contact.")
            return redirect('employer_profile:employer_profile_setup_step3')
        else:
            messages.error(request, "Please correct the errors.")
    else:
        form = EmployerProfileFoundingInfoForm(instance=profile)
        
    context = {
        'form': form,
        'step_title': "Founding Info",
        **get_setup_context(current_step),
    }
    return render(request, 'employer_profile/employer_profile_step2.html', context)


# --- Step 3 View: Contact (URL: employer/profile/contact/) ---
@login_required
def employer_profile_setup_step3(request):
    # redirect_check = check_employer_access(request.user)
    # if redirect_check: return redirect_check

    profile = get_object_or_404(EmployerProfile, user=request.user)
    current_step = 3
    
    if request.method == 'POST':
        form = EmployerProfileContactForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.setup_step = 4 
            profile.save()
            messages.success(request, "Contact Info saved. Profile is complete!")
            return redirect('employer_profile:employer_profile_completion')
        else:
            messages.error(request, "Please correct the errors.")
    else:
        form = EmployerProfileContactForm(instance=profile)
        
    context = {
        'form': form,
        'step_title': "Contact",
        **get_setup_context(current_step),
    }
    return render(request, 'employer_profile/employer_profile_step3.html', context)


# --- Final Completion View (URL: employer/profile/complete/) ---
@login_required
def employer_profile_completion(request):
    # redirect_check = check_employer_access(request.user)
    # if redirect_check: return redirect_check
    
    # We pass the full 100% completion context for the header
    return render(request, 'employer_profile/employer_profile_completion.html', {
        'is_setup_page': True, 
        'progress_percent': 100 
    })
