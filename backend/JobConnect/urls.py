#MyProject/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),  
    path('', include('JobConnectApp.urls')),
    path('applicant/', include('applicant_profile.urls')),
]
