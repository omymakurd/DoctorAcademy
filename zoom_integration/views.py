# في zoom_integration/views.py - استبدل المحتوى كاملاً بهذا:

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
import json
from .services_oauth import ZoomServiceOAuth  # ← استخدم الخدمة الجديدة

@csrf_exempt
@login_required
def create_zoom_meeting(request):
    """إنشاء اجتماع Zoom - للمدربين فقط"""
    # تحقق إذا المستخدم مدرب
    if not hasattr(request.user, 'instructor_profile'):
        return JsonResponse({
            'success': False,
            'error': 'يجب أن تكون مدرباً لإنشاء محاضرات'
        })
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # تحقق من البيانات المطلوبة
            if not data.get('start_time') or not data.get('duration'):
                return JsonResponse({
                    'success': False,
                    'error': 'الوقت والمدة مطلوبان'
                })
            
            zoom = ZoomServiceOAuth()
            meeting = zoom.create_meeting(
                topic=data.get('topic', 'محاضرة'),
                start_time=data['start_time'],
                duration=data['duration']
            )
            
            return JsonResponse({
                'success': True,
                'meeting': {
                    'id': meeting['id'],
                    'join_url': meeting['join_url'],
                    'start_url': meeting['start_url'],
                    'password': meeting.get('password', '123456')
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@login_required
def check_zoom_settings(request):
    """التحقق من إعدادات Zoom"""
    from django.conf import settings
    zoom_configured = all([
        settings.ZOOM_CLIENT_ID,
        settings.ZOOM_CLIENT_SECRET,
        settings.ZOOM_ACCOUNT_ID
    ])
    
    return JsonResponse({'zoom_configured': zoom_configured})

@login_required
def secure_zoom_join(request, lecture_id):
    """صفحة الانضمام الآمن للطلاب"""
    return render(request, 'zoom_integration/join_meeting.html', {
        'lecture_id': lecture_id
    })

@login_required
def secure_zoom_host(request, lecture_id):
    """صفحة المضيف الآمن للمدرب"""
    return render(request, 'zoom_integration/host_meeting.html', {
        'lecture_id': lecture_id
    })