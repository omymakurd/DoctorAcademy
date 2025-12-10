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

    AdminDevice.objects.update_or_create(
        user=request.user,
        defaults={"fcm_token": token}
    )

    return JsonResponse({"status": "ok"})
