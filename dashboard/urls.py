# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'   # <-- important: enables {% url 'dashboard:...' %} in templates

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Applicant URLs
    path('applicant/search-jobs/', views.ApplicantJobSearchView.as_view(), name='applicant_search_jobs'),
    path('applicant/applied-jobs/', views.ApplicantAppliedJobsListView.as_view(), name='applicant_applied_jobs'),
    path('applicant/favorite-jobs/', views.ApplicantFavoriteJobsView.as_view(), name='applicant_favorite_jobs'),
    path('applicant/job-alerts/', views.ApplicantJobAlertsView.as_view(), name='applicant_job_alerts'),
    path('applicant/job-alerts/create/', views.create_job_alert, name='create_job_alert'),
    path('applicant/job-alerts/<int:alert_id>/edit/', views.edit_job_alert, name='edit_job_alert'),
    path('applicant/job-alerts/<int:alert_id>/delete/', views.delete_job_alert, name='delete_job_alert'),
    path('applicant/job-alerts/<int:alert_id>/toggle/', views.toggle_job_alert_status, name='toggle_job_alert_status'),
    path('applicant/settings/', views.ApplicantSettingsView.as_view(), name='applicant_settings'),

    # Employer URLs
    path('employer/profile/', views.EmployerProfileView.as_view(), name='employer_profile'),
    path('employer/profile/<int:employer_id>/', views.public_employer_profile, name='public_employer_profile'),
    path('employer/settings/', views.EmployerSettingsView.as_view(), name='employer_settings'),
    path('employer/post-job/', views.EmployerPostJobView.as_view(), name='employer_post_job'),
    path('employer/edit-job/<int:job_id>/', views.EmployerEditJobView.as_view(), name='employer_edit_job'),
    path('employer/my-jobs/', views.EmployerJobListView.as_view(), name='employer_my_jobs'),
    path('employer/job-applications/<int:job_id>/', views.employer_job_applications, name='employer_job_applications'),
    path('employer/move-application/<int:application_id>/', views.move_application_stage, name='move_application_stage'),
    path('employer/candidate-detail/<int:application_id>/', views.employer_candidate_detail, name='employer_candidate_detail'),
    path('employer/hire-candidate/<int:application_id>/', views.hire_candidate, name='hire_candidate'),
    path('employer/toggle-save-candidate/<int:application_id>/', views.toggle_save_candidate, name='toggle_save_candidate'),
    path('employer/saved-candidates/', views.EmployerSavedCandidatesView.as_view(), name='employer_saved_candidates'),

    # Admin URLs
    path('admin/dashboards', views.admin_dashboards, name='admin_dashboards'),
    path('admin/total-employers-verified', views.admin_total_employers_verified, name='admin_total_employers_verified'),
    path('admin/accept-reject-employer', views.admin_accept_reject_employer, name='admin_accept_reject_employer'),
    path('admin/approve-employer/<int:employer_id>/', views.approve_employer, name='approve_employer'),
    path('admin/reject-employer/<int:employer_id>/', views.reject_employer, name='reject_employer'),
    path('admin/applicants', views.admin_applicants, name='admin_applicants'),
    path('admin/applicants/<int:applicant_id>/', views.admin_applicant_detail, name='admin_applicant_detail'),
    path('admin/job-postings', views.admin_job_postings, name='admin_job_postings'),
    path('admin/job-postings/<int:job_id>/', views.admin_job_detail, name='admin_job_detail'),
]
