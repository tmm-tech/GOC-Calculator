"""goc_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from goc_app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', views.logout_user, name='logout'),
    # Sysadmin URLs
    path('sysadmin/register/', views.register_sysadmin, name='register_sysadmin'),
    path('sysadmin/login/', views.login_sysadmin, name='login_sysadmin'),
    path('sysadmin/logout/', views.logout_sysadmin, name='logout_sysadmin'),
    path('sysadmin/register_user/', views.add_user, name='adminregister_user'),
    path('sysadmin/view_user/', views.view_users, name='view_users'),
    path('sysadmin/dashboard/', views.dashboard_admin, name='sysadmin_dashboard'),
    # Staff URLs
    path('staff/register/', views.register_staff, name='register_staff'),
    path('staff/login/', views.login_staff, name='login_staff'),
    path('staff/logout/', views.logout_staff, name='logout_staff'),
    path('staff/records/', views.view_records_staff, name='view_records_staff'),
    path('staff/register_users/', views.add_staff_user, name='staffregister_user'),
    path('staff/register_course/', views.add_course, name='add_course'),
    path('staff/dashboard/', views.dashboard_staff, name='staff_dashboard'),
    path('staff/update-record/<int:id>', views.update_record_staff, name='update_record_staff'),
    path('calculate_grade/', views.calculate_grade, name='calculate_grade'),


    # User URLs
    path('user/register/', views.register_user, name='register_user'),
    path('user/login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('user/dashboard/', views.dashboard, name='dashboard'),
    path('user/records/<str:username>', views.view_records_user, name='view_records_user'),
    path('user/calculate-gpa/<str:username>', views.calculate_gp, name='calculate_gp'),
    path('user/calculate-gpa/', views.calculate_gpa, name='calculate_gpa'),
]
