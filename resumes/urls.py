from django.urls import path
from . import views

app_name = 'resumes'

urlpatterns = [
    path('upload/', views.upload_resume, name='upload_resume'),
    path('delete/<int:resume_id>/', views.delete_resume, name='delete_resume'),
    path('set-default/<int:resume_id>/', views.set_default_resume, name='set_default_resume'),
]
