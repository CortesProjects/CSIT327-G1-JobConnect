# dashboards/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.models import User

@login_required
def dashboard_view(request):
    user = request.user
    if user.user_type == 'applicant':
        # The main dashboard view now renders the overview template.
        return render(request, 'dashboard/applicant/applicant_overview.html')
    elif user.user_type == 'employer':
        return render(request, 'dashboard/employer/employer_overview.html')
    elif user.user_type == 'admin':
        return render(request, 'dashboard/admin/admin_dashboards.html')
    else:
        # Fallback for any other user type or if user_type is not set
        return render(request, 'home.html')

@login_required
def applicant_applied_jobs(request):
    context = {} # Add any context needed for the template
    return render(request, 'dashboard/applicant/applicant_applied_jobs.html', context)

@login_required
def applicant_favorite_jobs(request):
    context = {} # Add any context needed for the template
    return render(request, 'dashboard/applicant/applicant_favorite_jobs.html', context)

@login_required
def applicant_job_alerts(request):
    context = {} # Add any context needed for the template
    return render(request, 'dashboard/applicant/applicant_job_alerts.html', context)

@login_required
def applicant_settings(request):
    return render(request, 'dashboard/applicant/applicant_settings.html')

@login_required
def employer_profile(request):
    return render(request, 'dashboard/employer/employer_profile.html')

@login_required
def post_job(request):
    return render(request, 'dashboard/employer/post_job.html')

@login_required
def my_jobs(request):
    return render(request, 'dashboard/employer/my_jobs.html')

@login_required
def employer_settings(request):
    return render(request, 'dashboard/employer/employer_settings.html')

#------------------------------------------
#              Admin Stuff
#------------------------------------------
@login_required
def admin_dashboards(request):
    total_verified_employers = User.objects.filter(user_type='employer', is_verified=True).count()
    total_unverified_employers = User.objects.filter(user_type='employer', is_verified=False).count()
    total_applicants = User.objects.filter(user_type='applicant').count()
    
    # Optional: count active job postings if needed
    # total_job_postings = JobPosting.objects.filter(is_active=True).count()

    context = {
        'total_verified_employers': total_verified_employers,
        'total_unverified_employers': total_unverified_employers,
        'total_applicants': total_applicants,
        # 'total_job_postings': total_job_postings,
    }
    return render(request, 'dashboard/admin/admin_dashboards.html', context)

@login_required
def admin_total_employers_verified(request):
    verified_employers = User.objects.filter(user_type='employer', is_verified=True).select_related('employer_profile_rel')

    context = {
        'verified_employers': verified_employers,
    }
    return render(request, "dashboard/admin/admin_total_employers_verified.html", context)

@login_required
def admin_accept_reject_employer(request):
    unverified_employers = User.objects.filter(user_type='employer', is_verified=False)

    context = {
        'unverified_employers': unverified_employers
    }
    return render(request, 'dashboard/admin/admin_accept_reject_employer.html', context)

@login_required
@user_passes_test(lambda u: u.user_type == 'admin')  # Only admins can approve
def approve_employer(request, employer_id):
    if request.method == 'POST':
        employer = get_object_or_404(User, id=employer_id, user_type='employer')
        employer.is_verified = True
        employer.save()
    return redirect('dashboard:admin_accept_reject_employer')

@login_required
def admin_applicants(request):
    applicants = User.objects.filter(user_type='applicant')
    context = {'applicants': applicants}
    return render(request, 'dashboard/admin/admin_applicants.html', context)

@login_required
def admin_job_postings(request):

    return render(request, "dashboard/admin/admin_job_postings.html")
#------------------------------------------
#          Admin Stuff Ends Here
# -----------------------------------------