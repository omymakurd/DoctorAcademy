# في zoom_integration/urls.py - تأكد أنه هكذا:

from django.urls import path
from . import views

urlpatterns = [
    path('create-meeting/', views.create_zoom_meeting, name='create_zoom_meeting'),
    path('check-settings/', views.check_zoom_settings, name='check_zoom_settings'),
    path('join/<int:lecture_id>/', views.secure_zoom_join, name='secure_zoom_join'),
    path('host/<int:lecture_id>/', views.secure_zoom_host, name='secure_zoom_host'),
]