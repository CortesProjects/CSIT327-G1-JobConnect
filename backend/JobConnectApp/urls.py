#MyApp/urls.py
from . import views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='homepage.html'), name='homepage'),
    path('admin_login/', views.admin_site, name='admin_login'),
    path('register/', views.register, name='register'),
    path('login/', views.login_site, name='login'),
    path('home/', views.home, name='home'),
    path("logout/", views.logout_view, name="logout"),
    path('base/', views.base, name='base'),
    path('admin_tab_1', views.admin_tab_1, name='admin_tab_1'),
    path('admin_tab_2', views.admin_tab_2, name='admin_tab_2'),
    path('admin_tab_3', views.admin_tab_3, name='admin_tab_3'),
    path('admin_tab_4', views.admin_tab_4, name='admin_tab_4'),
    path('admin_tab_5', views.admin_tab_5, name='admin_tab_5'),
]