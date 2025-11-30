from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from .forms import ApplicantRegistrationForm, UserLoginForm, EmployerRegistrationForm, CustomPasswordResetForm, CustomSetPasswordForm
from notifications.utils import create_notification
from django.contrib.auth import get_user_model

User = get_user_model() 


def get_user_dashboard_url(user):
    if user.is_staff or user.user_type == 'ADMIN':
        return '/dashboard/admin/dashboards'
    return 'dashboard:dashboard'


def home(request):
    """Home page view that redirects authenticated users to their dashboard"""
    if request.user.is_authenticated:
        return redirect(get_user_dashboard_url(request.user))
    # Provide dynamic site summary data for unauthenticated visitors
    try:
        from jobs.models import Job, JobCategory
        from django.db.models import Count

        live_jobs_count = Job.objects.filter(status='active').count()
        total_jobs_count = Job.objects.count()
        # Companies = registered employers
        companies_count = User.objects.filter(user_type='employer').count()
        candidates_count = User.objects.filter(user_type='applicant').count()

        # Popular categories by job count (top 8)
        popular_categories = JobCategory.objects.annotate(job_count=Count('jobs')).filter(job_count__gt=0).order_by('-job_count')[:8]

        # Featured jobs: recent active jobs
        featured_jobs = Job.objects.filter(status='active').annotate(applications_count=Count('applications')).order_by('-posted_at')[:3]

    except Exception:
        # Fallback to empty values if models are not available for any reason
        live_jobs_count = 0
        total_jobs_count = 0
        companies_count = 0
        candidates_count = 0
        popular_categories = []
        featured_jobs = []

    context = {
        'live_jobs_count': live_jobs_count,
        'total_jobs_count': total_jobs_count,
        'companies_count': companies_count,
        'candidates_count': candidates_count,
        'popular_categories': popular_categories,
        'featured_jobs': featured_jobs,
    }

    return render(request, 'home.html', context)


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
                
                # Notify all admin/superusers about new registration
                admin_users = User.objects.filter(is_staff=True, is_superuser=True)
                for admin in admin_users:
                    create_notification(
                        user=admin,
                        notification_type='system',
                        title='New User Registration',
                        message=f'New {user.user_type} registered: {user.email}',
                        link=f'/admin/accounts/user/{user.id}/change/',
                    )

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


# --- Password Reset Views ---
class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view with styled form"""
    form_class = CustomPasswordResetForm
    template_name = 'accounts/forgot_password.html'
    email_template_name = 'accounts/password_reset_email.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    
    def form_valid(self, form):
        messages.success(self.request, 'Password reset email has been sent if an account with that email exists.')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Custom password reset confirm view with styled form"""
    form_class = CustomSetPasswordForm
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been reset successfully!')
        return super().form_valid(form)
