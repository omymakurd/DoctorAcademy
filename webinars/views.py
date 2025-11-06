from django.shortcuts import render
from .models import Webinar

def upcoming_webinars(request):
    webinars = Webinar.objects.all()  # أو يمكنك إضافة ترتيب حسب التاريخ مثلاً
    return render(request, 'webinars/upcoming_webinars.html', {'webinars': webinars})
