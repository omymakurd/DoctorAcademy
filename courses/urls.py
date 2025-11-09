from django.urls import path
from . import views

app_name = "courses"   # ✅ أضف هذه

urlpatterns = [
    path('dashboard/', views.course_provider_dashboard, name='course_provider_dashboard'),
    path('provider/course/create/', views.course_create, name='course-create'),
    path('provider/course/<int:pk>/edit/', views.course_edit, name='course-edit'),
    path('provider/course/<int:pk>/delete/', views.course_delete, name='course-delete'),

    path('provider/course/<int:course_id>/units/', views.course_units, name='course-units'),
    path('provider/course/<int:course_id>/units/add/', views.create_unit, name='unit-add'),
    path('provider/unit/<int:unit_id>/edit/', views.edit_unit, name='unit-edit'),
    path('provider/unit/<int:unit_id>/delete/', views.delete_unit, name='unit-delete'),

    path('courses/', views.all_courses, name='all_courses'),
    path('course/<int:pk>/', views.course_detail, name='course_detail'),
  
    path('learn/<int:course_id>/', views.learn_course, name='learn_course'),
    path('unit/<int:unit_id>/complete/', views.complete_unit, name='complete_unit'),
    path('checkout/<int:course_id>/', views.checkout, name='checkout'),
    path('process/<int:course_id>/', views.process_checkout, name='process_checkout'),
    path('quiz/<int:quiz_id>/start/', views.start_quiz, name='quiz-start'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='quiz-take'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='quiz-submit'),
    path('quiz/<int:quiz_id>/result/<int:attempt_id>/', views.quiz_result, name='quiz-result'),
    path('quiz/<int:quiz_id>/history/', views.quiz_history, name='quiz-history'),
    path('quiz/<int:quiz_id>/autosave/<int:attempt_id>/', views.quiz_autosave, name='quiz-autosave'),
    path('provider/courses/', views.course_provider_courses, name='course_provider_courses'),
    path('provider/enrollments/', views.course_provider_enrollments, name='course_provider_enrollments'),
    path('revenue/', views.course_provider_revenue, name='course_provider_revenue'),  # <- مهم

]



