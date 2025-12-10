from django.urls import path
from . import views
app_name = 'lectures'
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
    path('module/<int:module_id>/checkout/', views.module_checkout, name='module_checkout'),
    path("instructor/my-lectures/", views.my_lectures, name="my_lectures"),
    path("module/<int:module_id>/edit/", views.edit_module, name="edit_module"),
    path('module/<int:module_id>/add/basic/', views.add_basic_lecture, name='add_basic_lecture'),
    path('module/<int:module_id>/add/clinical/', views.add_clinical_lecture, name='add_clinical_lecture'),
    path('module/<int:module_id>/learn/', views.module_learning_view, name='module_learning'),
    path('lecture/<int:lecture_id>/review/', views.add_review, name='add_review'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('quiz/<int:quiz_id>/<int:attempt_id>/autosave/', views.quiz_autosave, name='quiz-autosave'),
    path('quiz/<int:quiz_id>/submit/', views.quiz_submit, name='quiz-submit'),
    path('quiz/<int:quiz_id>/<int:attempt_id>/result/', views.quiz_result, name='quiz-result'),
    path('lecture/<str:lecture_type>/<int:lecture_id>/quiz-history/',views.quiz_history,name='quiz_lectuer_history'),
    path('module/<int:module_id>/delete/', views.delete_module, name='delete_module'),

    path('lecture/<str:lecture_type>/<int:lecture_id>/learn/', views.lecture_learning_view, name='lecture_learning'),
    path('instructor/lecture/<str:lecture_type>/<int:lecture_id>/quiz/add_page/', views.add_lecture_quiz_page, name='add_lecture_quiz_page'),
    path('module/edit/<int:pk>/', views.edit_module_modal, name='edit_module_modal'),
    path('module/manage/<int:module_id>/', views.module_manage, name='module_manage'),
    path('module/<int:module_id>/add-lecture-modal/', views.add_lecture_modal, name='add_lecture_modal'),
    path('module/<int:module_id>/save-lecture-order/', views.save_lecture_order, name='save_lecture_order'),
    path('lecture/<str:type>/<int:lecture_id>/', views.lecture_detail_modal, name='lecture_detail_modal'),
    # urls.py (اضف داخل urlpatterns)
    path('lecture/<str:lecture_type>/<int:lecture_id>/edit/', views.edit_lecture_ajax, name='edit_lecture_ajax'),
    path('lecture/<str:lecture_type>/<int:lecture_id>/delete/', views.delete_lecture_ajax, name='delete_lecture_ajax'),
   path("quiz/create/", views.create_quiz, name="create_quiz"),
   path("question/create/", views.create_question, name="create_question"),
   path("quiz/<int:quiz_id>/details/", views.quiz_details, name="quiz_details"),
   path("quiz/<int:quiz_id>/delete/", views.quiz_delete, name="quiz_delete"),
   path("question/<int:question_id>/edit/", views.question_edit, name="question_edit"),
   path("question/<int:question_id>/delete/", views.question_delete, name="question_delete"),
   path('case_study/create/', views.create_case_study, name='create_case_study'),
   path('case_study/<int:case_id>/edit/', views.edit_case_study, name='edit_case_study'),
   path('case_study/<int:case_id>/delete/', views.delete_case_study, name='delete_case_study'),

   # Placeholder pages for sidebar
    path("instructor/students/", views.students_list, name="students_list"),
    path("instructor/earnings/", views.instructor_earnings, name="instructor_earnings"),
    path("instructor/quizzes/", views.quizzes_overview, name="quizzes_overview"),
    path("instructor/cases/", views.case_studies_overview, name="case_studies_overview"),
    path("instructor/settings/", views.instructor_settings, name="instructor_settings"),
    
    path("lecture/<int:lecture_id>/comment/add/", views.add_comment, name="add_comment"),

    

    ]
