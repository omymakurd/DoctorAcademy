# zoom_integration/views_secure.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from lectures.models import BasicLecture, ZoomAccessLog
from .services import SecureZoomManager

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

@login_required
def secure_zoom_join(request, lecture_id):
    """رابط آمن للانضمام للطلاب"""
    lecture = get_object_or_404(BasicLecture, id=lecture_id)
    
    # تسجيل محاولة الدخول
    ZoomAccessLog.objects.create(
        user=request.user,
        lecture=lecture,
        action='attempted_join',
        ip_address=get_client_ip(request)
    )
    
    # إعادة التوجيه لرابط Zoom
    zoom_url = f"https://zoom.us/j/{lecture.zoom_meeting_id}"
    return redirect(zoom_url)

@login_required
def secure_zoom_host(request, lecture_id):
    """رابط آمن للمحاضر"""
    lecture = get_object_or_404(BasicLecture, id=lecture_id)
    
    if request.user != lecture.instructor:
        return render(request, 'zoom/access_denied.html')
    
    # تسجيل بدء المحاضرة
    ZoomAccessLog.objects.create(
        user=request.user,
        lecture=lecture,
        action='started_meeting', 
        ip_address=get_client_ip(request)
    )
    
    return redirect(lecture.zoom_start_url)