from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('add/basic/', views.add_basic_lecture, name='add_basic_lecture'),
    path('add/clinical/', views.add_clinical_lecture, name='add_clinical_lecture'),
    path('ajax/load-disciplines/', views.load_disciplines, name='ajax_load_disciplines'),
    path('instructor/module-wizard/', views.module_wizard, name='module_wizard'),
    path('instructor/module/add/', views.add_module, name='add_module'),  # AJAX Step 1
    path('instructor/module/<int:module_id>/lecture/add/', views.add_lecture, name='add_lecture'),  # AJAX Step 2
    path('instructor/lecture/<int:lecture_id>/quiz/add/', views.add_quiz, name='add_quiz'),
    path('instructor/lecture/<int:lecture_id>/case/add/', views.add_case_study, name='add_case_study'),
    path('instructor/quiz/<int:quiz_id>/question/add/', views.add_question, name='add_question'),
    path("modules/", views.module_list, name="module_list"),

    # صفحة تفاصيل موديول واحد
    path("modules/<int:module_id>/", views.module_detail, name="module_detail"),




]
