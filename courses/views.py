from django.shortcuts import render, redirect
from courses.models import Course
from django.contrib.auth.decorators import login_required

@login_required
def course_provider_dashboard(request):
    user = request.user

    # إجمالي الكورسات
    total_courses = Course.objects.filter(provider=user).count()

    # إجمالي الطلاب المسجلين
    total_enrollments = sum(c.enrollments.count() for c in Course.objects.filter(provider=user))

    # الإيرادات
    total_revenue = sum(c.price * c.enrollments.count() for c in Course.objects.filter(provider=user))

    # الطلاب النشطين
    total_students = len(set(
        s for c in Course.objects.filter(provider=user) for s in c.enrollments.all()
    ))

    # أحدث 5 كورسات
    latest_courses = Course.objects.filter(provider=user).order_by('-created_at')[:5]

    context = {
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'total_revenue': total_revenue,
        'total_students': total_students,
        'latest_courses': latest_courses,
    }

    return render(request, "course_provider_dashboard.html", context)
# courses/views.py
# courses/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Course, CourseUnit, Enrollment
from .forms import CourseForm, CourseUnitForm
from django.urls import reverse

# List courses of current provider

# Create a new course
@login_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.provider = request.user
            course.save()
            return redirect('courses:course_provider_dashboard')
    else:
        form = CourseForm()
    return render(request, 'course_form.html', {'form': form, 'create': True})

# Edit course
@login_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if course.provider != request.user:
        return HttpResponseForbidden("ليس لديك صلاحية تعديل هذا الكورس.")
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return redirect('courses:course_provider_dashboard')
    else:
        form = CourseForm(instance=course)
    return render(request, 'course_form.html', {'form': form, 'create': False, 'course': course})

# Delete course (optional)
@login_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if course.provider != request.user:
        return HttpResponseForbidden("ليس لديك صلاحية حذف هذا الكورس.")
    if request.method == 'POST':
        course.delete()
        return redirect('courses:provider-courses')
    return render(request, 'course_confirm_delete.html', {'course': course})

# Manage units for a course
@login_required
def course_units(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if course.provider != request.user:
        return HttpResponseForbidden("ليس لديك صلاحية إدارة وحدات هذا الكورس.")
    units = course.units.all().order_by('order')
    return render(request, 'course_units.html', {'course': course, 'units': units})

# Create unit
# Create unit

@login_required
def create_unit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if course.provider != request.user:
        return HttpResponseForbidden("ليس لديك صلاحية إضافة وحدات لهذا الكورس.")

    if request.method == 'POST':
        form = CourseUnitForm(request.POST, request.FILES)
        if form.is_valid():
            unit = form.save(commit=False)
            unit.course = course
            unit.save()
            return redirect(reverse('courses:course-units', args=[course.id]))
    else:
        form = CourseUnitForm()

    return render(request, 'unit_form.html', {'form': form, 'course': course, 'create': True})


@login_required
def edit_unit(request, unit_id):
    unit = get_object_or_404(CourseUnit, pk=unit_id)
    if unit.course.provider != request.user:
        return HttpResponseForbidden("ليس لديك صلاحية تعديل هذه الوحدة.")

    if request.method == 'POST':
        form = CourseUnitForm(request.POST, request.FILES, instance=unit)
        if form.is_valid():
            form.save()
            return redirect(reverse('courses:course-units', args=[unit.course.id]))
    else:
        form = CourseUnitForm(instance=unit)

    return render(request, 'unit_form.html', {'form': form, 'course': unit.course, 'unit': unit, 'create': False})

# Delete unit
@login_required
def delete_unit(request, unit_id):
    unit = get_object_or_404(CourseUnit, pk=unit_id)
    if unit.course.provider != request.user:
        return HttpResponseForbidden("ليس لديك صلاحية حذف هذه الوحدة.")
    course_id = unit.course.id
    if request.method == 'POST':
        unit.delete()
        return redirect(reverse('courses:course-units', args=[course_id]))
    return render(request, 'unit_confirm_delete.html', {'unit': unit})
