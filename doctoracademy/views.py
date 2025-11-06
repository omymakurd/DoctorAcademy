from django.shortcuts import render
from courses.models import Course
from lectures.models import Module, LectureCategory
from store.models import Product  # ← اضف هذا
from django.utils import timezone
from webinars.models import Webinar

def home(request):
    featured_courses = Course.objects.filter(featured=True, status='approved').order_by('-created_at')

    all_modules = Module.objects.filter(status__in=['approved', 'published'])[:8]
    basic_modules = [m for m in all_modules if m.basic_system][:4]
    clinical_modules = [m for m in all_modules if m.clinical_system][:4]

    # ✅ جلب منتجات للستور
    store_products = Product.objects.order_by('-created_at')[:4]
    webinars = Webinar.objects.filter(date__gte=timezone.now()).order_by('date')[:3]
    context = {
        "featured_courses": featured_courses,
        "basic_modules": basic_modules,
        "clinical_modules": clinical_modules,
        "store_products": store_products,
        "webinars": webinars,  # ← نرسل المنتجات للصفحة
    }

    return render(request, "home.html", context)
def faq(request):
    return render(request, "faq.html")

def help_center(request):
    return render(request, "help_center.html")

def contact(request):
    return render(request, "contact.html")
