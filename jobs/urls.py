from django.urls import path
from jobs import views

urlpatterns = [
    path('jobs/', views.user_job_list, name='user_job_list'),
    path('jobs/<int:job_id>/', views.user_job_detail, name='user_job_detail'),
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply_job'),

    path('upload-photo/', views.upload_profile_image, name='upload_photo'),
    path('profile/', views.user_profile, name='user_profile'),
    path('upload-resume/', views.upload_resume, name='upload_resume'),
    path('schedule-interview/<int:application_id>/', views.schedule_interview, name='schedule_interview'),
    path("schedule-interview/<int:application_id>/",views.schedule_interview,name="schedule_interview"
),
]   