from django.urls import path
from . import views

app_name = 'payments'  # ← مهم جدًا لتفعيل الـ namespace

urlpatterns = [
    path('stripe/start/<int:course_id>/', views.process_checkout, name='stripe_start'),
    path('courses/success/', views.payment_success, name='success'),
    path('courses/cancel/', views.payment_cancel, name='cancel'),
]
