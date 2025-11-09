from django.urls import path
from . import views

urlpatterns = [
    path('auth/', views.auth_view, name='auth'),  # صفحة تسجيل الدخول والتسجيل
    path('logout/', views.logout_view, name='logout'),  # تسجيل الخروج (اختياري)
   
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('api/progress_weekly/', views.api_progress_weekly, name='api_progress_weekly'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile_field, name='update_profile_field'),
    path('profile/update-photo/', views.update_profile_photo, name='update_profile_photo'),

]

