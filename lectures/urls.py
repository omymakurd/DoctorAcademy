from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('add/basic/', views.add_basic_lecture, name='add_basic_lecture'),
    path('add/clinical/', views.add_clinical_lecture, name='add_clinical_lecture'),
    path('ajax/load-disciplines/', views.load_disciplines, name='ajax_load_disciplines'),

]
