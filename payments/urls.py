from django.urls import path
from . import views

app_name = 'payments'  # ← مهم جدًا لتفعيل الـ namespace

urlpatterns = [
    path('stripe/start/<int:course_id>/', views.process_checkout, name='stripe_start'),
    path('courses/success/', views.payment_success, name='success'),
    path('courses/cancel/', views.payment_cancel, name='cancel'),
    path('stripe/start/basic/<int:lecture_id>/', views.process_checkout_basic, name='stripe_start_basic'),
    path('stripe/start/clinical/<int:lecture_id>/', views.process_checkout_clinical, name='stripe_start_clinical'),
    path('stripe/start/module/<int:module_id>/', views.process_checkout_module, name='stripe_start_module'),

]
