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

    # تأكد أن المستخدم مسجل بالكورس
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        return HttpResponseForbidden("You must enroll to access this course.")

    # الوحدات (الدروس)
    units = course.units.all().order_by("order")

    if not units.exists():
        return render(request, "course_no_content.html", {"course": course})

    # تحديد الدرس الحالي
    unit_id = request.GET.get("unit")
    if unit_id:
        current_unit = get_object_or_404(CourseUnit, id=unit_id, course=course)
    else:
        current_unit = units.first()

    # كويزات الوحدة الحالية
    quizzes = current_unit.quizzes.all()

    # التقدّم العام
    progress, _ = CourseProgress.objects.get_or_create(
        student=request.user,
        course=course
    )

    total_units = units.count()
    completed_unit_ids = list(progress.completed_units.values_list("id", flat=True))

    # 🧠 تحقق من الكويزات في الوحدة الحالية
    all_quizzes_completed = True
    for quiz in quizzes:
        last_attempt = quiz.attempts.filter(user=request.user).order_by("-started_at").first()
        if not last_attempt or not last_attempt.passed:
            all_quizzes_completed = False
            break

    # ✅ اعتبر الوحدة منتهية فقط إذا أنهى الكويزات أو ما فيها كويز
    if current_unit and (not quizzes.exists() or all_quizzes_completed):
        if current_unit.id not in completed_unit_ids:
            progress.completed_units.add(current_unit)
            progress.save()
            completed_unit_ids.append(current_unit.id)

    # النسبة
    completed_units = progress.completed_units.count()
    progress_percentage = int((completed_units / total_units) * 100) if total_units else 0

    # 🧩 معلومات تفصيلية لكل كويز
 # 🧮 بيانات الكويزات مع آخر محاولة
    quiz_data = []
    for quiz in quizzes:
        attempts = quiz.attempts.filter(user=request.user).order_by('-started_at')
        last_attempt = attempts.first() if attempts.exists() else None
        attempts_count = attempts.count()

        quiz_data.append({
            "quiz": quiz,
            "attempts": attempts,
            "last_attempt": last_attempt,
            "attempts_count": attempts_count,
        })


    # 🧭 حساب الدرس التالي
    next_unit = None
    unit_list = list(units)
    for index, unit in enumerate(unit_list):
        if unit.id == current_unit.id and index + 1 < len(unit_list):
            next_unit = unit_list[index + 1]
            break

    context = {
        "course": course,
        "units": units,
        "current_unit": current_unit,
        "quizzes": quizzes,
        "quiz_data": quiz_data,
        "progress_percentage": progress_percentage,
        "completed_unit_ids": completed_unit_ids,
        "next_unit": next_unit,  # 👈 الجديد المهم
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

# --- Quiz views (enhanced) ---
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from .models import Quiz, QuizAttempt, QuizAttemptDetail, Question, Choice
from django.urls import reverse

@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, published=True)
    attempts_done = QuizAttempt.objects.filter(user=request.user, quiz=quiz).count()
    if attempts_done >= quiz.max_attempts:
        return HttpResponseForbidden('No attempts left')

    attempt_number = attempts_done + 1
    attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz, attempt_number=attempt_number)
    return redirect('courses:quiz-take', quiz_id=quiz.id)


@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, published=True)
    attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz, is_submitted=False).order_by('-started_at').first()
    if not attempt:
        return redirect('courses:quiz-start', quiz_id=quiz.id)

    questions = list(quiz.questions.prefetch_related('choices').all())
    if quiz.randomize_questions:
        import random
        random.shuffle(questions)

    time_limit_seconds = quiz.time_limit * 60 if quiz.time_limit else None

    return render(request, 'quiz_take.html', {
        'quiz': quiz,
        'attempt': attempt,
        'questions': questions,
        'time_limit_seconds': time_limit_seconds,
    })


@login_required
@transaction.atomic
def submit_quiz(request, quiz_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)

    quiz = get_object_or_404(Quiz, id=quiz_id, published=True)
    attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz, is_submitted=False).order_by('-started_at').first()
    if not attempt:
        return JsonResponse({'error': 'Attempt not found or already submitted'}, status=404)

    # server-side time limit enforcement
    if quiz.time_limit:
        elapsed = (timezone.now() - attempt.started_at).total_seconds()
        if elapsed > quiz.time_limit * 60 + 5:
            attempt.is_submitted = True
            attempt.mark_finished()
            attempt.score = 0
            attempt.save()
            return JsonResponse({'status': 'timeout', 'message': 'Time limit exceeded'}, status=200)

    correct = 0
    total = quiz.questions.count()
    attempt.details.all().delete()

    for question in quiz.questions.all():
        selected_id = request.POST.get(f'question_{question.id}')
        selected_choice = None
        is_correct = False
        if selected_id:
            try:
                selected_choice = question.choices.get(id=int(selected_id))
                is_correct = selected_choice.is_correct
            except Exception:
                selected_choice = None
        if is_correct:
            correct += 1
        QuizAttemptDetail.objects.create(
            attempt=attempt,
            question=question,
            selected_choice=selected_choice,
            is_correct=is_correct
        )

    percentage = round((correct / total) * 100, 1) if total else 0
    attempt.score = percentage
    attempt.is_submitted = True
    attempt.mark_finished()
    attempt.save()

    passed = percentage >= quiz.pass_percentage
    return JsonResponse({'status': 'ok', 'score': percentage, 'passed': passed, 'attempt_id': attempt.id})


@login_required
def quiz_result(request, quiz_id, attempt_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    details = attempt.details.select_related('question', 'selected_choice').all()
    return render(request, 'quiz_result.html', {
        'quiz': quiz,
        'attempt': attempt,
        'details': details,
    })


@login_required
def quiz_history(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempts = QuizAttempt.objects.filter(user=request.user, quiz=quiz).order_by('-started_at')
    return render(request, 'quiz_history.html', {'quiz': quiz, 'attempts': attempts})


@login_required
def quiz_autosave(request, quiz_id, attempt_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user, is_submitted=False)
    attempt.details.all().delete()
    for key, value in request.POST.items():
        if not key.startswith('question_'):
            continue
        try:
            qid = int(key.split('_', 1)[1])
        except Exception:
            continue
        try:
            question = Question.objects.get(id=qid)
            selected_choice = question.choices.filter(id=int(value)).first() if value else None
            is_correct = selected_choice.is_correct if selected_choice else False
            QuizAttemptDetail.objects.create(
                attempt=attempt,
                question=question,
                selected_choice=selected_choice,
                is_correct=is_correct
            )
        except Question.DoesNotExist:
            continue
    return JsonResponse({'status': 'ok'})
@login_required
def course_provider_courses(request):
    # افتراضياً، نعرض الكورسات التي يمتلكها المستخدم الحالي
    courses = Course.objects.filter(provider=request.user)
    
    context = {
        'courses': courses
    }
    return render(request, 'course_provider_courses.html', context)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment  # افترض أنك لديك نموذج Enrollment

@login_required
def course_provider_enrollments(request):
    # جميع الطلاب المسجلين في كورسات هذا المحاضر
    enrollments = Enrollment.objects.filter(course__provider=request.user)
    
    context = {
        'enrollments': enrollments
    }
    return render(request, 'course_provider_enrollments.html', context)

# courses/views.py
from django.db.models import Sum, Count, Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Course

@login_required
def course_provider_revenue(request):
    provider = request.user

    courses = Course.objects.filter(provider=provider).annotate(
        paid_enrollments=Count('enrollments', filter=Q(enrollments__paid=True)),
        revenue=Sum('enrollments__course__price', filter=Q(enrollments__paid=True))
    )

    total_revenue = courses.aggregate(total=Sum('revenue'))['total'] or 0

    context = {
        'courses': courses,
        'total_revenue': total_revenue,
    }
    return render(request, 'course_provider_revenue.html', context)
