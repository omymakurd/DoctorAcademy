from django.shortcuts import render
from courses.models import Course
from lectures.models import Module, LectureCategory

def home(request):
    featured_courses = Course.objects.filter(featured=True, status='approved').order_by('-created_at')
    
    # جلب أي modules معتمدة/منشورة
    all_modules = Module.objects.filter(status__in=['approved', 'published'])[:8]
    
    # تقسيمها يدوياً بناءً على وجود النظام
    basic_modules = [m for m in all_modules if m.basic_system][:4]
    clinical_modules = [m for m in all_modules if m.clinical_system][:4]

    context = {
        "featured_courses": featured_courses,
        "basic_modules": basic_modules,
        "clinical_modules": clinical_modules,
    }
    return render(request, "home.html", context)