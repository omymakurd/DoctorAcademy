from django.urls import path
from . import views

app_name = "cases_new"

urlpatterns = [

    # ===== Instructor URLs =====
    path("instructor/", views.case_list, name="list"),
    path("instructor/create/", views.case_create, name="create"),
    path("instructor/edit/<int:pk>/", views.case_edit, name="edit"),
    path("instructor/detail/<int:pk>/", views.case_detail, name="detail"),
    path("instructor/delete/<int:pk>/", views.case_delete, name="delete"),
    #path("zoom/signature/",views.zoom_signature, name="zoom_signature"),
    path("zoom/signature/<int:pk>/", views.zoom_signature_endpoint, name="zoom_signature"),
    # ===== Student URLs =====
    path("student/", views.student_case_list, name="student_case_list"),
    path("student/<int:pk>/", views.student_case_detail, name="student_detail"),
]
