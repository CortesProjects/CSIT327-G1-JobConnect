from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import ApplicantRegistrationForm, UserLoginForm, EmployerRegistrationForm 


def get_user_dashboard_url(user):
    return 'dashboard:dashboard'


def home(request):
    """Home page view that redirects authenticated users to their dashboard"""
    if request.user.is_authenticated:
        return redirect(get_user_dashboard_url(request.user))
    return render(request, 'home.html')


def register(request):
    if request.user.is_authenticated:
        return redirect(get_user_dashboard_url(request.user)) 

    account_type_param = request.POST.get('account_type') or request.GET.get('account_type')
    account_type = account_type_param if account_type_param in ['applicant', 'employer'] else 'applicant'

    if account_type == 'employer':
        form_class = EmployerRegistrationForm  
    else:
        form_class = ApplicantRegistrationForm

    if request.method == 'POST':
        form = form_class(request.POST) 
        if form.is_valid():
            try:
                user = form.save()

                login(request, user)

                messages.success(
                    request,
                    f'Registration successful! Welcome to JobConnect as a {user.user_type.capitalize()}.'
                )

                if user.user_type == 'employer':
                    # FIX: Redirect to the new app's URL name
                    return redirect('employer_profile:employer_profile_setup_step1') 
                else:
                    # This should be the Applicant Setup start page
                    return redirect('applicant_profile:applicant_profile_setup_step1') 

            except IntegrityError as e:
                messages.error(request, "An account with this email already exists.")
            except Exception as e:
                messages.error(request, "An unexpected error occurred. Please contact support.")

        else:
            messages.error(request, "Please correct the errors in the form.")
    
    else:
        form = form_class(initial={'account_type': account_type})

    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect(get_user_dashboard_url(request.user)) 

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')

            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Handle 'Remember Me' logic
                if not remember_me:
                    request.session.set_expiry(0) 
                else:
                    request.session.set_expiry(60 * 60 * 24 * 14) 
                    
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name}!")
                next_url = request.POST.get('next')
                
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect(get_user_dashboard_url(user))
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Please correct the errors in the form.")
    
    else:
        form = UserLoginForm()
        
    next_url = request.GET.get('next')

    context = {
        'form': form,
        'next': next_url
    }
    return render(request, 'accounts/login.html', context)

# --- Logout View ---
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')
