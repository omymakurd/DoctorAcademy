from django.urls import path
from . import views

urlpatterns = [
    path('upcoming/', views.upcoming_webinars, name='upcoming_webinars'),
]
