from django.urls import path
from . import views

app_name = 'applicant_profile'

urlpatterns = [
    path('setup/personal-info/', views.applicant_profile_setup_step1, name='applicant_profile_setup_step1'),
    path('setup/education/', views.applicant_profile_setup_step2, name='applicant_profile_setup_step2'),
    path('setup/skills-resume/', views.applicant_profile_setup_step3, name='applicant_profile_setup_step3'),
    path('setup/complete/', views.applicant_profile_setup_complete, name='applicant_profile_setup_complete'),
]