from django.shortcuts import redirect
from django.contrib import messages


class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

       
        self.applicant_prefixes = (
            '/dashboard/applicant/settings',
            '/dashboard/applicant/job-alerts',
            '/dashboard/applicant/search-jobs',
            '/dashboard/applicant/favorite-jobs',
            '/dashboard/applicant/applied-jobs',
            '/applicant/setup/', 
        )
        
    
        self.applicant_job_actions = ('/favorite/', '/apply/')
        self.applicant_job_paths = ('/jobs/favorites/',)

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
            '/employer/setup/',  
        )
        
        self.employer_job_actions = ('/delete/', '/mark-expired/')
        
        self.employer_own_profile = '/dashboard/employer/profile/'

        self.admin_prefixes = (
            '/dashboard/admin/',
        )

    def __call__(self, request):
        path = request.path

        if not request.user.is_authenticated:
            return self.get_response(request)

        user_type = getattr(request.user, 'user_type', '')

        for pref in self.admin_prefixes:
            if path.startswith(pref):
                if not (request.user.is_staff or user_type == 'admin'):
                    messages.error(request, 'Access denied. Admin privileges required.')
                    return redirect('dashboard:dashboard')

        for pref in self.applicant_prefixes:
            if path.startswith(pref):
                if user_type != 'applicant':
                    messages.error(request, 'Access denied. Applicant account required.')
                    return redirect('dashboard:dashboard')
        
        if path.startswith('/jobs/'):
            for action in self.applicant_job_actions:
                if path.endswith(action):
                    if user_type != 'applicant':
                        messages.error(request, 'Access denied. Applicant account required.')
                        return redirect('dashboard:dashboard')
            
            for job_path in self.applicant_job_paths:
                if path.startswith(job_path):
                    if user_type != 'applicant':
                        messages.error(request, 'Access denied. Applicant account required.')
                        return redirect('dashboard:dashboard')
            
            for action in self.employer_job_actions:
                if path.endswith(action):
                    if user_type != 'employer':
                        messages.error(request, 'Access denied. Employer account required.')
                        return redirect('dashboard:dashboard')

        for pref in self.employer_prefixes:
            if path.startswith(pref):
                if user_type != 'employer':
                    messages.error(request, 'Access denied. Employer account required.')
                    return redirect('dashboard:dashboard')
        
        if path == self.employer_own_profile:
            if user_type != 'employer':
                messages.error(request, 'Access denied. Employer account required.')
                return redirect('dashboard:dashboard')

        return self.get_response(request)
