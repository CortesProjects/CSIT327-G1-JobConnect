#dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    # Applicant URLs
    path('applicant/applied-jobs/', views.applicant_applied_jobs, name='applicant_applied_jobs'),
    path('applicant/favorite-jobs/', views.applicant_favorite_jobs, name='applicant_favorite_jobs'),
    path('applicant/job-alerts/', views.applicant_job_alerts, name='applicant_job_alerts'),
    path('applicant/settings/', views.applicant_settings, name='applicant_settings'),
    # Employer URLs
    path('employer/profile/', views.employer_profile, name='employer_profile'),
    path('employer/settings/', views.employer_settings, name='employer_settings'),
    path('employer/post-job/', views.employer_post_job, name='employer_post_job'),
    path('employer/my-jobs/', views.employer_my_jobs, name='employer_my_jobs'),
    path('employer/settings/', views.employer_settings, name='employer_settings'),
    path('employer/job-applications/', views.employer_job_applications, name='employer_job_applications'),
    path('employer/candidate-detail/', views.employer_candidate_detail, name='employer_candidate_detail'),
    # Admin URLs
    path('admin_tab_1', views.admin_dashboards, name='admin_dashboards'),
    path('admin_tab_2', views.admin_total_employers_verified, name='admin_total_employers_verified'),
    path('admin_tab_3', views.admin_accept_reject_employer, name='admin_accept_reject_employer'),
    path('admin/approve-employer/<int:employer_id>/', views.approve_employer, name='approve_employer'),
    path('admin_tab_4', views.admin_applicants, name='admin_applicants'),
    path('admin_tab_5', views.admin_job_postings, name='admin_job_postings'),
    
]
