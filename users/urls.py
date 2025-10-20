from django.urls import path
from . import views

urlpatterns = [
    path('auth/', views.auth_view, name='auth'),  # صفحة تسجيل الدخول والتسجيل
    path('logout/', views.logout_view, name='logout'),  # تسجيل الخروج (اختياري)
]