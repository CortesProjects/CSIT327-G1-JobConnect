from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.job_search, name='job_search'),
    path('suggestions/', views.job_suggestions, name='job_suggestions'),
]