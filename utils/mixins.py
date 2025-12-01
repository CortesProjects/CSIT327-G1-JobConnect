"""
Custom mixins for access control and common view functionality.
These mixins leverage Django's UserPassesTestMixin for role-based access control.
Also includes decorator versions for function-based views.
"""
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from functools import wraps
from django.contrib.auth.decorators import login_required


# Decorator versions for function-based views
def employer_required(view_func):
    """
    Decorator that requires the user to be authenticated and have employer user type.
    Use this instead of manually checking user_type in function-based views.
    
    Usage:
        @employer_required
        def my_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if request.user.user_type != 'employer':
            messages.error(request, 'Access denied. Employer account required.')
            return redirect('dashboard:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapped_view


def applicant_required(view_func):
    """
    Decorator that requires the user to be authenticated and have applicant user type.
    Use this instead of manually checking user_type in function-based views.
    
    Usage:
        @applicant_required
        def my_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if request.user.user_type != 'applicant':
            messages.error(request, 'Access denied. Applicant account required.')
            return redirect('dashboard:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapped_view


def admin_required(view_func):
    """
    Decorator that requires the user to be authenticated and be an admin/staff user.
    Use this instead of manually checking is_staff in function-based views.
    
    Usage:
        @admin_required
        def my_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if not (request.user.is_staff or request.user.user_type == 'admin'):
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapped_view


class EmployerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin that requires the user to be authenticated and have employer user type.
    Redirects to login if not authenticated, or shows error if wrong user type.
    """
    login_url = reverse_lazy('accounts:login')
    
    def test_func(self):
        return self.request.user.user_type == 'employer'
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, 'Access denied. Employer account required.')
        return redirect('dashboard:dashboard')


class ApplicantRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin that requires the user to be authenticated and have applicant user type.
    Redirects to login if not authenticated, or shows error if wrong user type.
    """
    login_url = reverse_lazy('accounts:login')
    
    def test_func(self):
        return self.request.user.user_type == 'applicant'
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, 'Access denied. Applicant account required.')
        return redirect('dashboard:dashboard')


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin that requires the user to be authenticated and be an admin/staff user.
    Redirects to login if not authenticated, or shows error if not admin.
    """
    login_url = reverse_lazy('accounts:login')
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.user_type == 'admin'
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, 'Access denied. Admin privileges required.')
        return redirect('dashboard:dashboard')


class JobOwnerRequiredMixin(UserPassesTestMixin):
    """
    Mixin that requires the user to be the owner of the job being accessed.
    Use with views that have a job object (e.g., DetailView, UpdateView).
    """
    def test_func(self):
        job = self.get_object()
        return job.employer == self.request.user
    
    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access this job.')
        return redirect('dashboard:employer_my_jobs')


class AjaxResponseMixin:
    """
    Mixin to add AJAX response capabilities to class-based views.
    Detects AJAX requests and returns JSON instead of rendering HTML.
    """
    def is_ajax(self):
        return (
            self.request.headers.get('x-requested-with') == 'XMLHttpRequest' or
            'application/json' in self.request.META.get('HTTP_ACCEPT', '')
        )
    
    def form_valid(self, form):
        """Override to provide JSON response for AJAX requests."""
        response = super().form_valid(form)
        
        if self.is_ajax():
            from django.http import JsonResponse
            return JsonResponse({
                'success': True,
                'message': getattr(self, 'success_message', 'Operation completed successfully'),
                'redirect_url': self.get_success_url()
            })
        return response
    
    def form_invalid(self, form):
        """Override to provide JSON error response for AJAX requests."""
        response = super().form_invalid(form)
        
        if self.is_ajax():
            from django.http import JsonResponse
            errors = form.errors.get_json_data()
            error_message = 'Invalid form submission'
            
            if '__all__' in errors:
                error_message = errors['__all__'][0]['message']
            elif errors:
                first_field = next(iter(errors))
                error_message = errors[first_field][0]['message']
            
            return JsonResponse({
                'success': False,
                'error': error_message,
                'errors': form.errors
            }, status=400)
        return response
