from django.urls import path
from jobs import views

urlpatterns = [
    path('list/', views.user_job_list, name='job_list'),
    path('<int:pk>/', views.user_job_detail, name='job_detail'),
    path('<int:pk>/apply/', views.user_apply_job, name='apply_job'),

    path('jobs/', views.user_job_list, name='user_job_list'),
    path('jobs/<int:job_id>/', views.user_job_detail, name='user_job_detail'),
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply_job'),

]
