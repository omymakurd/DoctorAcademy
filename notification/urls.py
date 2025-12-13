from django.urls import path
from . import views

urlpatterns = [
   path('save-fcm-token/', views.save_fcm_token),
   path('admin-notifications/', views.admin_notifications, name='admin_notifications'),
   path('unread-count/', views.unread_count, name='unread_count'),
   path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
   path('mark-read/<int:notif_id>/', views.mark_read, name='mark_read'),


]
