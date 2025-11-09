# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import User, StudentProfile, InstructorProfile, CourseProviderProfile
from courses.models import Enrollment, CourseProgress

from lectures.models import LectureProgress, QuizAttempt
from payments.models import Payment
def auth_view(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # =========================
        # تسجيل دخول
        # =========================
        if action == "login":
            username = request.POST.get("username")
            password = request.POST.get("password")

            # السماح بتسجيل الدخول بالـ username أو الـ email
            user = authenticate(request, username=username, password=password)
            if not user:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user:
                login(request, user)
                messages.success(request, "Welcome back!")

                # تحويل حسب الدور
                if user.role == "instructor":
                    return redirect("lectures:instructor_dashboard")
                elif user.role == "student":
                    return redirect("student_dashboard")
                elif user.role == "course_provider":
                    return redirect("courses:course_provider_dashboard")
                else:
                    return redirect("home")
            else:
                messages.error(request, "Invalid credentials. Please try again.")

        # =========================
        # إنشاء حساب
        # =========================
        elif action == "signup":
            username = request.POST.get("username")
            email = request.POST.get("email")
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")
            role = request.POST.get("role")

            if password1 != password2:
                messages.error(request, "Passwords do not match.")
                return redirect("auth")

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return redirect("auth")

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return redirect("auth")

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                role=role,
            )

            # إنشاء البروفايل حسب الدور
            if role == "student":
                StudentProfile.objects.create(user=user)
            elif role == "instructor":
                InstructorProfile.objects.create(user=user)
            elif role == "course_provider":
                CourseProviderProfile.objects.create(user=user)

            messages.success(request, "Account created successfully.")

            # تحويل المستخدم حسب الدور
            login(request, user)
            if role == "instructor":
                return redirect("instructor_dashboard")
            elif role == "student":
                return redirect("student_dashboard")
            elif role == "course_provider":
                return redirect("courses:course_provider_dashboard")

            else:
                return redirect("home")

    return render(request, "auth.html",{})


def logout_view(request):
    """
    تسجيل خروج المستخدم
    """
    logout(request)
    messages.info(request, "👋 You have been logged out.")
    return redirect('auth')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

# استدعاءات لموديلاتك الحالية - تأكد أن المسارات صحيحة
from courses.models import Enrollment, CourseProgress
from lectures.models import LectureProgress
from lectures.models import Module
from lectures.models import BasicLecture, ClinicalLecture
from lectures.models import ModuleProgress
from lectures.models import QuizAttempt
from lectures.models import Certificate

@login_required
def student_dashboard(request):
    user = request.user

    # enrollments: جميع الدورات / الموديولات التي اشترك بها المستخدم
    enrollments = Enrollment.objects.filter(student=user).select_related('course')  # قم بالتعديل إن تستخدم ModuleEnrollment

    # Lecture progress
    lecture_progress = LectureProgress.objects.filter(student=user).select_related('basic_lecture', 'clinical_lecture')

    # Course progress
    course_progress_qs = CourseProgress.objects.filter(student=user).select_related('course')

    # Quiz attempts (الأحدث أولاً)
    quiz_attempts = QuizAttempt.objects.filter(student=user).select_related('quiz').order_by('-started_at')[:10]

    # Certificates
    certificates = Certificate.objects.filter(student=user).order_by('-issued_at')[:10]

    # حساب متوسط التقدم (avg_progress) عبر ModuleProgress أو CourseProgress
    # نستخدم ModuleProgress إذا متوفر، وإلا نحسب من CourseProgress
    module_progress_qs = ModuleProgress.objects.filter(student=user)
    if module_progress_qs.exists():
        avg_progress = round(sum([mp.progress_percentage for mp in module_progress_qs]) / module_progress_qs.count(), 0)
    else:
        # fallback: من CourseProgress (نحسب نسبة كاملة من completed_units / total_units)
        vals = []
        for cp in course_progress_qs:
            total_units = cp.course.units.count() if hasattr(cp.course, 'units') else 0
            completed = cp.completed_units.count() if hasattr(cp, 'completed_units') else 0
            pct = (completed / total_units * 100) if total_units else 0
            vals.append(pct)
        avg_progress = round(sum(vals) / len(vals), 0) if vals else 0

    # map of course.id -> progress% (لمعرفة داخل القالب)
    progress_map = {}
    for cp in course_progress_qs:
        total_units = cp.course.units.count() if hasattr(cp.course, 'units') else 0
        completed = cp.completed_units.count() if hasattr(cp, 'completed_units') else 0
        prog = int((completed / total_units * 100)) if total_units else 0
        progress_map[cp.course.id] = prog

    context = {
        'enrollments': enrollments,
        'lecture_progress': lecture_progress,
        'course_progress': course_progress_qs,
        'quiz_attempts': quiz_attempts,
        'certificates': certificates,
        'avg_progress': avg_progress,
        'progress_map': progress_map,
    }
    return render(request, 'users/student_dashboard.html', context)


# API endpoint returning weekly progress chart data
@login_required
def api_progress_weekly(request):
    user = request.user
    today = timezone.localdate()
    labels = []
    values = []
    # last 7 days
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        labels.append(day.strftime('%a'))  # اختصر اسم اليوم
        # حساب بسيط: عدد الوحدات المكتملة في هذا اليوم / إجمالي وحدات اليوم (تقريب)
        # أفضل طريقة: تسجيل UnitView مع تاريخ viewed_at ثم count per day
        from lectures.models import UnitView
        completed_today = UnitView.objects.filter(student=user, viewed_at__date=day).count()
        # لتحويل رقم ل% نحتاج مقياس (مثلاً 5 views = 100%) → هنا نستخدم مقياس مرن
        # نضبط denominator = أقصى عدد وحدات شاهدها خلال يوم في آخر 7 أيام أو 1 لتجنب القسمة على صفر
        values.append(completed_today)
    # نريد قياساً نسبياً من 0..100: نطبع numbers raw ثم الـ frontend يمكن يعالجها
    return JsonResponse({'labels': labels, 'values': values})

# users/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def profile(request):
    user = request.user

    # حقول عامة للمستخدم
    account_fields = [
        {'field': 'full_name', 'label': 'Full Name'},
        {'field': 'phone', 'label': 'Phone'},
    ]

    # حقول StudentProfile
    student_fields = [
        {'field': 'university', 'label': 'University'},
        {'field': 'year', 'label': 'Year'},
    ]

    # حقول InstructorProfile
    instructor_fields = [
        {'field': 'specialization', 'label': 'Specialization'},
        {'field': 'linkedin', 'label': 'LinkedIn'},
    ]

    # حقول CourseProviderProfile
    provider_fields = [
        {'field': 'entity_name', 'label': 'Entity Name'},
        {'field': 'bank_name', 'label': 'Bank Name'},
        {'field': 'iban', 'label': 'IBAN'},
    ]

    # دالة مساعدة للحصول على البيانات من أي بروفايل
    def get_profile_data(profile, fields):
        if not profile:
            return {}
        return {field['field']: getattr(profile, field['field'], None) for field in fields}

    # تجهيز البيانات لكل بروفايل
    student_data = get_profile_data(getattr(user, 'student_profile', None), student_fields)
    instructor_data = get_profile_data(getattr(user, 'instructor_profile', None), instructor_fields)
    provider_data = get_profile_data(getattr(user, 'provider_profile', None), provider_fields)

    return render(request, 'users/profile.html', {
        'user': user,
        'account_fields': account_fields,
        'student_fields': student_fields,
        'instructor_fields': instructor_fields,
        'provider_fields': provider_fields,
        'student_data': student_data,
        'instructor_data': instructor_data,
        'provider_data': provider_data,
    })


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, StudentProfile, InstructorProfile, CourseProviderProfile

@csrf_exempt
def update_profile_field(request):
    if request.method == "POST" and request.user.is_authenticated:
        field = request.POST.get('field')
        value = request.POST.get('value')

        user = request.user

        # تحديث الحقول على User
        if field in ['full_name', 'phone']:
            if field == 'full_name':
                user.first_name = value.split()[0] if value else ''
                user.last_name = ' '.join(value.split()[1:]) if len(value.split()) > 1 else ''
            else:
                user.phone = value
            user.save()
            return JsonResponse({'status': 'success', 'value': value})

        # تحديث StudentProfile
        if hasattr(user, 'student_profile') and field in ['university', 'year']:
            profile = user.student_profile
            setattr(profile, field, value)
            profile.save()
            return JsonResponse({'status': 'success', 'value': value})

        # تحديث InstructorProfile
        if hasattr(user, 'instructor_profile') and field in ['specialization', 'linkedin']:
            profile = user.instructor_profile
            setattr(profile, field, value)
            profile.save()
            return JsonResponse({'status': 'success', 'value': value})

        # تحديث CourseProviderProfile
        if hasattr(user, 'provider_profile') and field in ['entity_name', 'bank_name', 'iban']:
            profile = user.provider_profile
            setattr(profile, field, value)
            profile.save()
            return JsonResponse({'status': 'success', 'value': value})

        return JsonResponse({'status': 'error', 'message': 'Invalid field'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@csrf_exempt
@login_required
def update_profile_photo(request):
    if request.method == "POST":
        user = request.user
        photo = request.FILES.get('photo')

        if not photo:
            return JsonResponse({'status':'error', 'message':'No file uploaded'})

        # تحقق من وجود InstructorProfile أو أنشئ واحد إذا لم يوجد
        profile, created = getattr(user, 'instructor_profile', None), False
        if not profile:
            # يمكنك تعديلها حسب نوع المستخدم، مثال: إنشاء InstructorProfile إذا لم يوجد
            from .models import InstructorProfile
            profile = InstructorProfile.objects.create(user=user)
            created = True

        profile.photo = photo
        profile.save()
        return JsonResponse({'status':'success', 'url': profile.photo.url})

    return JsonResponse({'status':'error', 'message':'Invalid request'})
