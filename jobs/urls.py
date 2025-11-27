from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.job_search, name='job_search'),
    path('suggestions/', views.job_suggestions, name='job_suggestions'),
    path('<int:job_id>/favorite/', views.toggle_favorite_job, name='toggle_favorite_job'),
    path('favorites/', views.applicant_favorite_jobs, name='applicant_favorite_jobs'),
]