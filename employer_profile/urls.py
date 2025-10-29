from django.urls import path
from . import views

app_name = 'employer_profile'

urlpatterns = [
    path('setup/company-info/', views.employer_profile_setup_step1, name='employer_profile_setup_step1'),
    path('setup/founding-info/', views.employer_profile_setup_step2, name='employer_profile_setup_step2'),
    path('setup/contact/', views.employer_profile_setup_step3, name='employer_profile_setup_step3'),
    path('setup/complete/', views.employer_profile_completion, name='employer_profile_completion'),
]