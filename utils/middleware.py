from django.shortcuts import redirect
from django.contrib import messages


class RoleBasedAccessMiddleware:
    """Middleware to enforce role-based access for dashboard routes.

    This provides a last-resort enforcement layer so views are protected
    even if decorators/mixins are accidentally bypassed.
    """
    def __init__(self, get_response):
        self.get_response = get_response

        # Define protected prefixes per role (exact path prefixes under /dashboard/)
        self.applicant_prefixes = (
            '/dashboard/applicant/settings',
            '/dashboard/applicant/job-alerts',
            '/dashboard/applicant/search-jobs',
            '/dashboard/applicant/favorite-jobs',
            '/dashboard/applicant/applied-jobs',
        )

        self.employer_prefixes = (
            '/dashboard/employer/settings',
            '/dashboard/employer/post-job',
            '/dashboard/employer/edit-job',
            '/dashboard/employer/my-jobs',
            '/dashboard/employer/job-applications',
            '/dashboard/employer/move-application',
            '/dashboard/employer/candidate-detail',
            '/dashboard/employer/hire-candidate',
            '/dashboard/employer/toggle-save-candidate',
            '/dashboard/employer/saved-candidates',
        )

        self.admin_prefixes = (
            '/dashboard/admin/',
        )

    def __call__(self, request):
        path = request.path

        # If not authenticated, let auth middleware handle redirects
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Admin-only paths
        for pref in self.admin_prefixes:
            if path.startswith(pref):
                if not (request.user.is_staff or getattr(request.user, 'user_type', '') == 'admin'):
                    messages.error(request, 'Access denied. Admin privileges required.')
                    return redirect('dashboard:dashboard')

        # Applicant-only paths
        for pref in self.applicant_prefixes:
            if path.startswith(pref):
                if getattr(request.user, 'user_type', '') != 'applicant':
                    messages.error(request, 'Access denied. Applicant account required.')
                    return redirect('dashboard:dashboard')

        # Employer-only paths
        for pref in self.employer_prefixes:
            if path.startswith(pref):
                if getattr(request.user, 'user_type', '') != 'employer':
                    messages.error(request, 'Access denied. Employer account required.')
                    return redirect('dashboard:dashboard')

        return self.get_response(request)
