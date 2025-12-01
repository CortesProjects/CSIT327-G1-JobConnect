from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('search/', views.job_search, name='job_search'),
    path('suggestions/', views.job_suggestions, name='job_suggestions'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('<int:job_id>/favorite/', views.toggle_favorite_job, name='toggle_favorite_job'),
    path('<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('<int:job_id>/mark-expired/', views.mark_job_expired, name='mark_job_expired'),
]