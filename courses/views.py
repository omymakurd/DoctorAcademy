from django.shortcuts import render, redirect
from courses.models import Course
from django.contrib.auth.decorators import login_required
from .models import CourseProgress
from .models import CourseReview

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
def all_courses(request):
    courses = Course.objects.filter(status='approved')

    # ===== Search Filter =====
    search = request.GET.get('search')
    if search:
        courses = courses.filter(title__icontains=search)

    # ===== Price Filter =====
    price = request.GET.get('price')
    if price == "free":
        courses = courses.filter(price=0)
    elif price == "paid":
        courses = courses.filter(price__gt=0)

    # ===== Featured Filter =====
    featured = request.GET.get('featured')
    if featured == "true":
        courses = courses.filter(featured=True)

    # ===== Sorting =====
    sort = request.GET.get('sort')
    if sort == "latest":
        courses = courses.order_by('-created_at')
    elif sort == "oldest":
        courses = courses.order_by('created_at')
    elif sort == "price_high":
        courses = courses.order_by('-price')
    elif sort == "price_low":
        courses = courses.order_by('price')

    return render(request, 'all_courses.html', {'courses': courses})

def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    is_enrolled = False

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()

    context = {
        'course': course,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'course_detail.html', context)



@login_required
def learn_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        return HttpResponseForbidden("You must enroll to access this course.")

    units = course.units.all().order_by('order')

    if not units.exists():
        return render(request, "course_no_content.html", {"course": course})

    unit_id = request.GET.get("unit")
    if unit_id:
        current_unit = get_object_or_404(CourseUnit, id=unit_id, course=course)
    else:
        current_unit = units.first()

    # ✅ جلب الكويزات التابعة للوحدة الحالية
    quizzes = current_unit.quizzes.all()  # Assuming related_name="quizzes" in model

    progress, _ = CourseProgress.objects.get_or_create(
        student=request.user,
        course=course
    )

    if current_unit and not progress.completed_units.filter(id=current_unit.id).exists():
        progress.completed_units.add(current_unit)
        progress.save()

    total_units = units.count()
    completed_units = progress.completed_units.count()
    progress_percentage = int((completed_units / total_units) * 100) if total_units else 0

    context = {
        "course": course,
        "units": units,
        "current_unit": current_unit,
        "quizzes": quizzes,   # ✅ أضفنا هذا
        "progress_percentage": progress_percentage,
    }

    return render(request, "learn_course.html", context)

@login_required
def complete_unit(request, unit_id):
    unit = get_object_or_404(CourseUnit, id=unit_id)
    progress = CourseProgress.objects.get(student=request.user, course=unit.course)
    progress.completed_units.add(unit)
    progress.save()
    return JsonResponse({"status": "success"})
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment
from django.http import HttpResponseForbidden

@login_required
def checkout(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # إذا مسجل مسبقًا → دخله مباشرة للكورس
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        return redirect('courses:learn_course', course_id=course.id)

    # كورس مجاني → سجل فورًا
    if course.price == 0:
        Enrollment.objects.get_or_create(student=request.user, course=course)
        return redirect('courses:learn_course', course_id=course.id)

    # كورس مدفوع → اعرض صفحة اختيار طريقة الدفع
    return render(request, 'checkout.html', {'course': course})


@login_required
def process_checkout(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    payment_method = request.POST.get("payment_method")

    if course.price == 0:
        Enrollment.objects.get_or_create(student=request.user, course=course)
        return redirect("courses:learn_course", course.id)

    # PayMob
    if payment_method == "paymob":
        return redirect(f"/pay/paymob/start/{course.id}")

    # Stripe
    elif payment_method == "stripe":
        return redirect(f"/pay/stripe/start/{course.id}")

    # PayPal
    elif payment_method == "paypal":
        return redirect(f"/pay/paypal/start/{course.id}")

    return redirect('courses:checkout', course_id=course.id)

from django.shortcuts import get_object_or_404, redirect, render
from .models import CourseUnit, Quiz
from django.contrib import messages
from .models import QuizAttempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Quiz, QuizAttempt, CourseUnit, Choice

@login_required
def take_quiz_inline(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    unit = quiz.unit
    course = unit.course

    # عدد المحاولات
    attempts = QuizAttempt.objects.filter(user=request.user, quiz=quiz).count()

    if attempts >= quiz.max_attempts:
        return render(request, "quiz_result_review.html", {
            "quiz": quiz,
            "passed": False,
            "remaining_attempts": 0,
            "score": 0,
            "total": quiz.questions.count(),
            "user_answers": {},
            "correct_answers": {q.id: q.get_correct_choice().text for q in quiz.questions.all()},
            "percentage": 0
        })

    if request.method == "POST":
        correct = 0
        user_answers = {}

        for question in quiz.questions.all():
            selected_id = request.POST.get(f"question_{question.id}")
            if selected_id:
                selected_choice = question.choices.get(id=selected_id)
                user_answers[question.id] = selected_choice.text
                if selected_choice.is_correct:
                    correct += 1
            else:
                user_answers[question.id] = "No answer"

        total = quiz.questions.count()
        score = correct
        percentage = round((correct / total) * 100, 1)

        QuizAttempt.objects.create(user=request.user, quiz=quiz, score=percentage)

        passed = percentage >= quiz.pass_percentage

        correct_answers = {q.id: q.get_correct_choice().text for q in quiz.questions.all()}

        remaining_attempts = quiz.max_attempts - (attempts + 1)

        # إذا نجح → نعدي الوحدة
        if passed:
            progress, _ = CourseProgress.objects.get_or_create(student=request.user, course=course)
            progress.completed_units.add(unit)

        return render(request, "quiz_review.html", {
            "quiz": quiz,
            "passed": passed,
            "score": score,
            "total": total,
            "percentage": percentage,
            "user_answers": user_answers,
            "correct_answers": correct_answers,
            "remaining_attempts": max(remaining_attempts, 0)
        })

    return render(request, "quiz_inline.html", {"quiz": quiz})
