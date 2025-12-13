from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import AdminDevice



@csrf_exempt
@login_required
def save_fcm_token(request):
    data = json.loads(request.body)
    token = data.get("token")
    from .models import AdminDevice
    AdminDevice.objects.get_or_create(user=request.user, fcm_token=token)
    return JsonResponse({"status": "ok"})

import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification
@login_required
def admin_notifications(request):
    if not request.user.is_staff:
        return redirect('home')

    notifs = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'admin_notifications.html', {'notifications': notifs})

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification

@login_required
def unread_count(request):
    return JsonResponse({
        "count": Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
    })
@login_required
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"status": "ok"})

@login_required
def mark_read(request, notif_id):
    Notification.objects.filter(id=notif_id, recipient=request.user).update(is_read=True)
    return JsonResponse({"status": "ok"})

