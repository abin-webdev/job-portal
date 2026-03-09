from django.urls import path
from accounts import views

urlpatterns = [

    # ---------------- AUTH ---------------- #
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Role redirect
    path('redirect/', views.role_redirect, name='role_redirect'),

    # Company second-step registration
    path('company/register/', views.company_register, name='company_register'),

    # ---------------- USER ---------------- #
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/applications/', views.user_applications, name='user_applications'),
    path('user/jobs/', views.user_job_list, name='user_job_list'),
    path('user/job/<int:job_id>/apply/', views.apply_job, name='apply_job'),

    # ---------------- COMPANY ---------------- #
    path('company/dashboard/', views.company_dashboard, name='company_dashboard'),
    path('company/jobs/', views.company_jobs, name='company_jobs'),
    path('company/post-job/', views.company_post_job, name='company_post_job'),
    path(
        'company/job/<int:job_id>/applications/',
        views.company_applications,
        name='company_applications'
    ),
    path(
        'company/application/<int:app_id>/approve/',
        views.company_approve,
        name='company_approve'
    ),
    path(
        'company/application/<int:app_id>/reject/',
        views.company_reject,
        name='company_reject'
    ),

    # ---------------- ADMIN ---------------- #
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Users
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/delete/', views.admin_delete_user, name='admin_delete_user'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # Companies
    path('admin/companies/', views.admin_companies, name='admin_companies'),
    path('admin/companies/<int:company_id>/delete/', views.admin_delete_company, name='admin_delete_company'),
    path("company/job/<int:job_id>/applications/",views.company_applications,name="company_job_applications"),
    path("company/application/<int:app_id>/",views.company_application_detail,name="company_application_detail",),
    path("company/application/<int:app_id>/approve/",views.company_approve,name="company_approve",),
    path("company/application/<int:app_id>/reject/",views.company_reject,name="company_reject",),
    path("admin/companies/<int:company_id>/delete/",views.admin_delete_company,name="admin_delete_company"),
    path("company/register/", views.company_register, name="company_register"),



    # Admin

    path('admin/jobs/', views.admin_job_list, name='admin_job_list'),
    path('admin/jobs/<int:pk>/delete/', views.admin_delete_job, name='admin_delete_job'),

    # Applications
    path('admin/applications/', views.admin_applications, name='admin_applications'),
]

