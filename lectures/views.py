from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from lectures.models import BasicLecture, ClinicalLecture
from courses.models import Course
from cases.models import CaseStudy
from users.models import User
from lectures.models import LectureProgress
from .models import BasicLecture, ClinicalLecture
from .forms import BasicLectureForm, ClinicalLectureForm
from django.http import JsonResponse
from .models import Discipline
from django.utils.translation import gettext as _
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Avg, F
from django.http import JsonResponse
from django.utils import timezone
import datetime
import json
@login_required
def instructor_dashboard(request):
    user = request.user

    # counts
    lectures_count = BasicLecture.objects.filter(instructor=user).count() + ClinicalLecture.objects.filter(instructor=user).count()

    # students active (distinct)
    students_basic = User.objects.filter(lecture_progress__basic_lecture__in=BasicLecture.objects.filter(instructor=user)).distinct()
    students_clinical = User.objects.filter(lecture_progress__clinical_lecture__in=ClinicalLecture.objects.filter(instructor=user)).distinct()
    active_students_count = (students_basic | students_clinical).distinct().count()

    # recent activity
    recent_progress = LectureProgress.objects.filter(
        basic_lecture__in=BasicLecture.objects.filter(instructor=user)
    ).order_by('-completed_at')[:10]

    # earnings (use Payment model)
    total_earnings = Payment.objects.filter(module__in=Module.objects.filter(instructor=user), status='completed').aggregate(total=Sum('amount'))['total'] or 0

    # average rating
    avg_rating = LectureReview.objects.filter(
        basic_lecture__in=BasicLecture.objects.filter(instructor=user)
    ).aggregate(avg=Avg('rating'))['avg'] or 0

    # top lectures by completion %
    top_lectures = []
    basic_lects = BasicLecture.objects.filter(instructor=user).annotate(
    total = Count('module__basiclectures')
)[:10]

    # a robust way:
    for lec in BasicLecture.objects.filter(instructor=user):
        total = LectureProgress.objects.filter(basic_lecture=lec).count()
        completed = LectureProgress.objects.filter(basic_lecture=lec, status='completed').count()
        percent = int((completed / total * 100) if total else 0)
        top_lectures.append({
            'title': lec.title,
            'module_title': lec.module.title if lec.module else '',
            'completed': completed,
            'total': total,
            'complete_percent': percent
        })
    top_lectures = sorted(top_lectures, key=lambda x: x['complete_percent'], reverse=True)[:5]

    # revenue data for last N days (default 30)
    days = int(request.GET.get('days', 30))
    today = timezone.now().date()
    start = today - datetime.timedelta(days=days-1)
    daily = Payment.objects.filter(created_at__date__gte=start, created_at__date__lte=today, status='completed', module__in=Module.objects.filter(instructor=user))\
        .extra({'day': "date(created_at)"}).values('day').annotate(total=Sum('amount')).order_by('day')

    # prepare arrays for chart labels/data
    labels = []
    data = []
    day_map = {d['day'].isoformat(): float(d['total']) for d in daily}
    for i in range(days):
        d = start + datetime.timedelta(days=i)
        labels.append(d.strftime('%d %b'))
        data.append(day_map.get(d.isoformat(), 0))

    context = {
        'lectures_count': lectures_count,
        'students_count': active_students_count,
        'cases_count': CaseStudy.objects.filter(created_by=user).count(),
        'recent_progress': recent_progress,
        'lecture_labels': [l['title'] for l in top_lectures],
        'lecture_data': [l['complete_percent'] for l in top_lectures],
        'student_labels': [], 'student_data': [],
        'primary_color': '#0056D2',
        'accent_color': '#FFA000',
        'total_earnings': total_earnings,
        'avg_rating': round(avg_rating, 2),
        'top_lectures': top_lectures,
        'revenue_labels_json': json.dumps(labels),
        'revenue_data_json': json.dumps(data),
        'revenue_labels': labels,
        'revenue_data': data,
        'currency': 'USD',
        'earnings_change_percent': 12,
    }
    return render(request, 'instructor_dashboard.html', context)


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .forms import ModuleForm
from .models import Module

@login_required
def add_module(request):
    if request.user.role != "instructor":
        return JsonResponse({'success': False, 'errors': 'Not authorized'})

    if request.method == 'POST':
        form = ModuleForm(request.POST, request.FILES)
        if form.is_valid():
            module = form.save(commit=False)
            module.instructor = request.user
            module.status = 'pending'  # يروح للمراجعة
            module.save()

            # ✅ تعديل هنا: نرجّع اسم الموديول عشان الجافاسكربت يعرضه بالستيب الثانية
            return JsonResponse({
                'success': True,
                'module_id': module.id,
                'module_name': str(module),  # أو module.title لو عندك حقل اسمه title
            })

        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'errors': 'Invalid request'})



from zoom_integration.utils import create_zoom_meeting_for_lecture
from django.utils import timezone


@login_required
def add_lecture(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    form_class = BasicLectureForm if module.basic_system else ClinicalLectureForm

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.module = module
            lecture.instructor = request.user
            
            # 🔵 معالجة محاضرات الزوم - النسخة الآمنة
            if lecture.lecture_type == 'zoom':
                try:
                    from zoom_integration.services import SecureZoomManager
                    zoom_manager = SecureZoomManager()
                    
                    meeting_data = zoom_manager.create_secure_meeting(lecture)
                    
                    # حفظ بيانات Zoom
                    lecture.zoom_meeting_id = meeting_data['id']
                    lecture.zoom_join_url = f"/zoom/join/{lecture.id}/"  # رابط آمن
                    lecture.zoom_start_url = meeting_data['start_url']
                    
                except Exception as e:
                    return JsonResponse({
                        'success': False, 
                        'errors': f'فشل إنشاء اجتماع Zoom: {str(e)}'
                    })
            
            lecture.save()
            return JsonResponse({'success': True, 'lecture_id': lecture.id})
        
        return JsonResponse({'success': False, 'errors': form.errors})
@login_required
def add_quiz(request, lecture_id):
    lecture = BasicLecture.objects.filter(id=lecture_id).first() or ClinicalLecture.objects.filter(id=lecture_id).first()
    if not lecture:
        return JsonResponse({'success': False, 'errors': 'Lecture not found'})

    if request.method == 'POST':
        title = request.POST.get('title')
        if not title:
            return JsonResponse({'success': False, 'errors': 'Title is required.'})

        # تحديد نوع المحاضرة
        if isinstance(lecture, BasicLecture):
            quiz = Quiz.objects.create(
                lecture_type='basic',
                basic_lecture=lecture,
                title=title
            )
        else:
            quiz = Quiz.objects.create(
                lecture_type='clinical',
                clinical_lecture=lecture,
                title=title
            )
        return JsonResponse({'success': True, 'quiz_id': quiz.id})

    
    return JsonResponse({'success': False, 'errors': 'Invalid request'})

from .models import Quiz, Question, Choice


@login_required
def add_question(request, quiz_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'errors': 'Invalid request method'})

    quiz = get_object_or_404(Quiz, id=quiz_id)

    question_text = request.POST.get('text', '').strip()
    correct_answer = request.POST.get('correct_answer', '').strip()
    choices = request.POST.getlist('choices[]', [])
    correct_index = request.POST.get('correct_choice')

    if not question_text:
        return JsonResponse({'success': False, 'errors': 'Question text is required.'})
    if not correct_answer and not choices:
        return JsonResponse({'success': False, 'errors': 'You must provide a correct answer or choices.'})

    # إنشاء السؤال
    question = Question.objects.create(
        quiz=quiz,
        text=question_text,
        correct_answer=correct_answer
    )

    # إذا فيه خيارات، أضفها
    if choices:
        try:
            correct_index = int(correct_index)
        except (ValueError, TypeError):
            correct_index = -1

        for i, choice_text in enumerate(choices):
            Choice.objects.create(
                question=question,
                text=choice_text.strip(),
                is_correct=(i == correct_index)
            )

    return JsonResponse({'success': True, 'question_id': question.id})
from cases.forms import CaseStudyForm
import traceback

@login_required
def add_case_study(request, lecture_id):
    try:
        # الكود الأصلي هنا
        basic_lecture = BasicLecture.objects.filter(id=lecture_id).first()
        clinical_lecture = ClinicalLecture.objects.filter(id=lecture_id).first()

        if not basic_lecture and not clinical_lecture:
            return JsonResponse({'success': False, 'errors': 'Lecture not found'})

        if request.method == 'POST':
            form = CaseStudyForm(request.POST, request.FILES)
            if form.is_valid():
                case = form.save(commit=False)
                case.created_by = request.user
                if basic_lecture:
                    case.basic_lecture = basic_lecture
                    case.discipline = basic_lecture.discipline
                elif clinical_lecture:
                    case.clinical_lecture = clinical_lecture
                    case.discipline = clinical_lecture.discipline
                case.save()
                return JsonResponse({'success': True, 'case_id': case.id})
            else:
                return JsonResponse({'success': False, 'errors': form.errors})
        return JsonResponse({'success': False, 'errors': 'Invalid request method.'})

    except Exception as e:
        return JsonResponse({'success': False, 'errors': str(e), 'trace': traceback.format_exc()})

@login_required
def add_basic_lecture(request):
    if request.user.role != "instructor":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': "You are not authorized."})
        return redirect('home')

    if request.method == 'POST':
        form = BasicLectureForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.instructor = request.user
            lecture.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': "Lecture added successfully!"})
            return redirect('instructor_dashboard')
        else:
            errors = form.errors.as_json()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': "Please correct the errors.", 'errors': errors})
            return render(request, 'add_basic_lecture.html', {'form': form})
    else:
        form = BasicLectureForm(user=request.user)

    return render(request, 'add_basic_lecture.html', {'form': form})
@login_required
def module_wizard(request):
    if request.user.role != "instructor":
        return redirect('home')

    module_form = ModuleForm()
    lecture_form = BasicLectureForm(user=request.user)

    # 🔹 أضف هذا السطر
    modules = Module.objects.filter(instructor=request.user).order_by('-created_at')

    return render(request, 'add_module_wizerd.html', {
        'module_form': module_form,
        'lecture_form': lecture_form,
        'modules': modules,  # ✅ تمرير القائمة
    })


@login_required
def add_clinical_lecture(request, module_id):
    if not request.user.is_instructor:
        return JsonResponse({'success': False, 'errors': 'Not authorized'}, status=403)

    module = get_object_or_404(Module, id=module_id)

    if request.method == 'POST':
        form = ClinicalLectureForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.instructor = request.user
            lecture.module = module  # ربط المحاضرة بالـ module
            lecture.save()

            # 🔹 هنا نعيد JSON وليس redirect
            return JsonResponse({
                "success": True,
                "lecture_id": lecture.id,
                "lecture_type": "clinical"
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = ClinicalLectureForm(user=request.user)

    return render(request, 'add_clinical_lecture.html', {'lecture_form': form, 'module': module})

@login_required
def load_disciplines(request):
    system_id = request.GET.get('system_id')
    disciplines = Discipline.objects.filter(system_id=system_id).values('id', 'name')
    return JsonResponse(list(disciplines), safe=False)

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@login_required
@csrf_exempt
def create_zoom_meeting_for_lecture(request, lecture_id):
    from zoom_integration.views import create_zoom_meeting
    res = create_zoom_meeting(request)
    data = res.json()

    if "join_url" in data:
        lecture = BasicLecture.objects.get(id=lecture_id)
        lecture.zoom_link = data["join_url"]
        lecture.zoom_meeting_id = data["id"]
        lecture.zoom_join_url = data["join_url"]
        lecture.zoom_start_url = data["start_url"]
        lecture.save()
    return JsonResponse(data)
from django.shortcuts import render, get_object_or_404
from .models import Module, BasicSystem, ClinicalSystem

from django.shortcuts import render
from .models import Module, BasicSystem, ClinicalSystem, Discipline

def module_list(request):
    modules = Module.objects.filter(status__in=["approved", "published"])

    # ----- Search -----
    search = request.GET.get("search")
    if search:
        modules = modules.filter(title__icontains=search)

    # ----- Price -----
    price = request.GET.get("price")
    if price == "free":
        modules = modules.filter(price=0)
    elif price == "paid":
        modules = modules.filter(price__gt=0)

    # ----- Basic / Clinical -----
    system_type = request.GET.get("type")
    if system_type == "basic":
        modules = modules.filter(basic_system__isnull=False)
    elif system_type == "clinical":
        modules = modules.filter(clinical_system__isnull=False)

    # ----- Filter by System -----
    system_id = request.GET.get("system")
    if system_id:
        modules = modules.filter(basic_system_id=system_id) | modules.filter(clinical_system_id=system_id)

    # ----- Filter by Discipline -----
    discipline_id = request.GET.get("discipline")
    if discipline_id:
        # فلترة حسب النوع لأن الموديل لا يحتوي على حقل discipline مباشر
        if system_type == "basic":
            modules = modules.filter(basic_system_id=discipline_id)
        elif system_type == "clinical":
            modules = modules.filter(clinical_system_id=discipline_id)

    # ----- Featured -----
    featured = request.GET.get("featured")
    if featured == "true":
        modules = modules.filter(is_featured=True)

    # ----- Sorting -----
    sort = request.GET.get("sort")
    if sort == "latest":
        modules = modules.order_by("-created_at")
    elif sort == "oldest":
        modules = modules.order_by("created_at")
    elif sort == "price_low":
        modules = modules.order_by("price")
    elif sort == "price_high":
        modules = modules.order_by("-price")

    # ----- Dropdown data -----
    basic_systems = BasicSystem.objects.all()
    clinical_systems = ClinicalSystem.objects.all()
    disciplines = Discipline.objects.all()

    return render(request, "module_list.html", {
        "modules": modules,
        "basic_systems": basic_systems,
        "clinical_systems": clinical_systems,
        "disciplines": disciplines,
    })

from django.shortcuts import render, get_object_or_404
from .models import Module

def module_detail(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    user_enrolled = False

    if request.user.is_authenticated:
        user_enrolled = module.enrollments.filter(student=request.user).exists()

    context = {
        "module": module,
        "user_enrolled": user_enrolled
    }
    return render(request, "module_detail.html", context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Module, ModuleEnrollment, PaymentTransaction

@login_required
def module_checkout(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    # هل الطالب مسجّل مسبقاً؟
    user_enrolled = ModuleEnrollment.objects.filter(
        student=request.user,
        module=module
    ).exists()

    if request.method == "POST" and not user_enrolled:
        # تسجيل الطالب في الموديول
        ModuleEnrollment.objects.create(
            student=request.user,
            module=module,
            purchased_price=module.price
        )

        # سجل دفع (اختياري الآن)
        PaymentTransaction.objects.create(
            user=request.user,
            module=module,
            amount=module.price,
            status="success"
        )

        messages.success(request, "Payment Completed ✅ You are now enrolled.")
        return redirect('lectures:module_detail', module_id=module.id)


    return render(request, 'module_checkout.html', {
        'module': module,
        'user_enrolled': user_enrolled
    })
@login_required
def my_lectures(request):
    modules = Module.objects.filter(instructor=request.user).order_by('-created_at')
    return render(request, "my_lectures.html", {"modules": modules})

from .forms import ModuleForm

@login_required
def edit_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        total_duration = request.POST.get('total_duration_minutes')
        basic_system_id = request.POST.get('basic_system')
        clinical_system_id = request.POST.get('clinical_system')
        thumbnail = request.FILES.get('thumbnail')

        # تحديث البيانات
        module.title = title
        module.description = description
        module.price = price
        module.total_duration_minutes = total_duration

        # تحديث الأنظمة
        if basic_system_id:
            module.basic_system = BasicSystem.objects.get(id=basic_system_id)
            module.clinical_system = None  # تعطيل الآخر
        elif clinical_system_id:
            module.clinical_system = ClinicalSystem.objects.get(id=clinical_system_id)
            module.basic_system = None  # تعطيل الآخر
        else:
            module.basic_system = None
            module.clinical_system = None

        # تحديث الصورة إذا تم رفعها
        if thumbnail:
            module.thumbnail = thumbnail

        module.save()  # ✅ هذا هو السطر الذي يحفظ التعديلات

        messages.success(request, "Module updated successfully!")
        return redirect('lectures:module_manage', module_id=module.id)

    # لو أحد دخل بالـ GET نعيده للصفحة الأساسية
    return redirect('lectures:module_manage', module_id=module.id)

@login_required
def delete_module(request, module_id):
    module = get_object_or_404(Module, id=module_id, instructor=request.user)
    module.delete()
    messages.success(request, "Module Deleted ✅")
    return redirect('lectures:my_lectures')
@login_required
def add_basic_lecture(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    if request.method == 'POST':
        form = BasicLectureForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.instructor = request.user
            lecture.module = module     # ✅ ربطها بالموديول
            lecture.save()
            return redirect('lectures:module_detail', module_id=module.id)
    else:
        form = BasicLectureForm(user=request.user)

    return render(request, 'add_basic_lecture.html', {'form': form, "module": module})
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Module, ClinicalLecture

from django.http import JsonResponse

@login_required
def add_clinical_lecture(request, module_id):
    module = get_object_or_404(Module, id=module_id, instructor=request.user)
    
    if request.method == "POST":
        form = ClinicalLectureForm(request.POST, request.FILES, user=request.user, module_instance=module)
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.instructor = request.user
            lecture.module = module
            lecture.save()
            
            # لو أردت إضافة الفيديو/attachments هنا أي شيء إضافي
            # lecture.video_file = form.cleaned_data.get('video_file')
            # lecture.save()
            
            # رجع JSON للـAJAX
            return JsonResponse({"success": True, "lecture_id": lecture.id})
        else:
            # يمكن طباعة الأخطاء في الكونسول
            print(form.errors)
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
    else:
        form = ClinicalLectureForm(user=request.user, module_instance=module)

    return render(request, 'add_clinical_lecture.html', {'lecture_form': form, 'module': module})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Module, BasicLecture, ClinicalLecture
from payments.models import Payment

@login_required
def module_learning_view(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    # التأكد من تسجيل الطالب في الموديول
    if not module.enrollments.filter(student=request.user).exists():
        return redirect('lectures:module_detail', module_id=module.id)

    # جلب جميع المحاضرات
    basic_lectures = list(BasicLecture.objects.filter(module=module))
    clinical_lectures = list(ClinicalLecture.objects.filter(module=module))
    all_lectures = basic_lectures + clinical_lectures

    # تحديد المحاضرة الحالية
    lecture_id = request.GET.get("lecture")
    current_lecture = None
    next_lecture = None

    if lecture_id:
        for idx, lec in enumerate(all_lectures):
            if str(lec.id) == lecture_id:
                current_lecture = lec
                if idx + 1 < len(all_lectures):
                    next_lecture = all_lectures[idx + 1]
                break
    elif all_lectures:
        current_lecture = all_lectures[0]
        if len(all_lectures) > 1:
            next_lecture = all_lectures[1]

    # ✅ التحقق من الدفع لكل نوع محاضرة
    if current_lecture:
        payment_exists = Payment.objects.filter(
            student=request.user,
            status='completed',
            **({'lecture_clinical': current_lecture} if isinstance(current_lecture, ClinicalLecture)
               else {'lecture_basic': current_lecture})
        ).exists()

        if not payment_exists:
            # تحويل الطالب إلى صفحة الدفع المناسبة
            if isinstance(current_lecture, ClinicalLecture):
                return redirect('payments:stripe_start_clinical', current_lecture.id)
            else:
                return redirect('payments:stripe_start_basic', current_lecture.id)

    # حساب نسبة التقدم
    completed = request.user.lecture_progress.filter(
        Q(basic_lecture__in=basic_lectures) |
        Q(clinical_lecture__in=clinical_lectures),
        status="completed"
    ).count()
    total_lectures = len(all_lectures)
    progress_percentage = (completed / total_lectures * 100) if total_lectures else 0

    context = {
        "module": module,
        "basic_lectures": basic_lectures,
        "clinical_lectures": clinical_lectures,
        "current_lecture": current_lecture,
        "next_lecture": next_lecture,
        "progress_percentage": progress_percentage,
    }
    return render(request, "module_learning.html", context)

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import BasicLecture, ClinicalLecture, LectureReview

@login_required
def add_review(request, lecture_id):
    if request.method != "POST":
        return redirect("lectures:module_list")  # أو أي صفحة مناسبة

    lecture_type = request.POST.get("lecture_type")
    
    if lecture_type == "basic":
        lecture = get_object_or_404(BasicLecture, id=lecture_id)
    elif lecture_type == "clinical":
        lecture = get_object_or_404(ClinicalLecture, id=lecture_id)
    else:
        # إذا نوع المحاضرة غير صحيح، نرجع المستخدم للصفحة العامة
        return redirect("lectures:module_list")  

    rating = request.POST.get("rating")
    comment = request.POST.get("comment", "")

    if lecture_type == "basic":
        LectureReview.objects.create(
            student=request.user,
            basic_lecture=lecture,
            rating=rating,
            comment=comment
        )
    else:
        LectureReview.objects.create(
            student=request.user,
            clinical_lecture=lecture,
            rating=rating,
            comment=comment
        )

    # بعد الإضافة نرجع المستخدم للصفحة الصحيحة
    return redirect(f"/lectures/module/{lecture.module.id}/learn/?lecture={lecture.id}")
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Quiz, Question, Choice, QuizAttempt, QuizAnswer
@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # أنشئ Attempt جديد أو استرجع الحالي
    attempt, created = QuizAttempt.objects.get_or_create(
        student=request.user, quiz=quiz, defaults={'attempt_number': quiz.attempts.count() + 1}
    )
    
    questions = quiz.questions.all()
    
    # مثال وقت محدود 10 دقائق (600 ثواني)
    time_limit_seconds = quiz.time_limit_seconds if hasattr(quiz, 'time_limit_seconds') else None

    context = {
        "quiz": quiz,
        "questions": questions,
        "attempt": attempt,
        "time_limit_seconds": time_limit_seconds
    }
    return render(request, "take_quiz_advanced.html", context)

@login_required
def quiz_autosave(request, quiz_id, attempt_id):
    if request.method == "POST":
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
        for key, value in request.POST.items():
            if key.startswith("question_"):
                qid = int(key.replace("question_", ""))
                question = get_object_or_404(Question, id=qid)
                choice = get_object_or_404(question.choices, id=int(value))
                ans, _ = QuizAnswer.objects.update_or_create(
                    attempt=attempt, question=question,
                    defaults={'selected_choice': choice}
                )
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "fail"}, status=400)

@login_required
def quiz_submit(request, quiz_id):
    if request.method == "POST":
        quiz = get_object_or_404(Quiz, id=quiz_id)
        attempt = get_object_or_404(QuizAttempt, quiz=quiz, student=request.user)
        # يمكنك هنا حساب النقاط
        score = 0
        for ans in attempt.answers.all():
            if ans.selected_choice.is_correct:
                score += 1
        attempt.score = score
        attempt.completed = True
        attempt.save()
        return JsonResponse({"status": "ok", "attempt_id": attempt.id})
    return JsonResponse({"status": "fail"}, status=400)


def quiz_result(request, quiz_id, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    return render(request, "quiz_lectuer_result.html", {"attempt": attempt})


from django.shortcuts import render, get_object_or_404
from .models import BasicLecture, ClinicalLecture, Quiz, QuizAttempt
@login_required
def quiz_history(request, lecture_type, lecture_id):
    """
    lecture_type: 'basic' أو 'clinical'
    """
    if lecture_type == 'basic':
        lecture = get_object_or_404(BasicLecture, id=lecture_id)
        quizzes = lecture.quizzes.all()
    elif lecture_type == 'clinical':
        lecture = get_object_or_404(ClinicalLecture, id=lecture_id)
        quizzes = lecture.quizzes.all()
    else:
        return render(request, "error.html", {"message": "Invalid lecture type"})

    # جميع المحاولات الخاصة بالمستخدم لكل الكويزات
    attempts = QuizAttempt.objects.filter(quiz__in=quizzes, student=request.user).order_by('-started_at')

    return render(request, "quiz_lectuer_history.html", {
        "lecture": lecture,
        "quizzes": quizzes,
        "attempts": attempts,
        "lecture_type": lecture_type
    })
# في lectures/views.py (أضف الاستيرادات أعلى الملف)
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from .utils import user_has_access_to_lecture
from payments.models import Payment

@login_required
def lecture_learning_view(request, lecture_type, lecture_id):
    """
    lecture_type: 'basic' أو 'clinical'
    هذه الصفحة تعرض المحاضرة فردياً (player, resources, quiz links)
    إن لم يكن عند المستخدم دفع، نعيده لصفحة الدفع المناسبة.
    """
    if lecture_type == 'basic':
        lecture = get_object_or_404(BasicLecture, id=lecture_id)
    elif lecture_type == 'clinical':
        lecture = get_object_or_404(ClinicalLecture, id=lecture_id)
    else:
        return HttpResponseForbidden("Invalid lecture type")

    # إذا المحاضرة مجانية (price == 0 أو None) نسمح بالدخول.
    # ملاحظة: حسب موديلك، قد تحتاج تضيف حقل price في BasicLecture / ClinicalLecture
    price = getattr(lecture, 'price', None)
    is_free = (price is None) or (price == 0)

    if not is_free:
        # تحقق الدفع
        if not user_has_access_to_lecture(request.user, lecture):
            # Redirect to lecture-specific checkout route (routes موجودة عندك)
            if lecture_type == 'basic':
                return redirect('payments:stripe_start_basic', lecture_id=lecture.id)
            else:
                return redirect('payments:stripe_start_clinical', lecture_id=lecture.id)

    # لو وصل هنا، إما مجانية أو مُدفع لها
    context = {
        'lecture': lecture,
        'lecture_type': lecture_type,
    }
    return render(request, 'lecture_learning.html', context)



from django.shortcuts import get_object_or_404, redirect
from .models import Module
from django.contrib.auth.decorators import login_required

@login_required
def delete_module(request, module_id):
    module = get_object_or_404(Module, id=module_id, instructor=request.user)
    if request.method == "POST":
        module.delete()
        return redirect('lectures:my_lectures')
    return render(request, 'confirm_delete_module.html', {'module': module})

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import BasicLecture, ClinicalLecture, Quiz, Question, Choice
from .forms import QuizForm, QuestionFormSet, ChoiceFormSet

@login_required
def add_lecture_quiz_page(request, lecture_type, lecture_id):
    if lecture_type == 'basic':
        lecture = get_object_or_404(BasicLecture, id=lecture_id)
    elif lecture_type == 'clinical':
        lecture = get_object_or_404(ClinicalLecture, id=lecture_id)
    else:
        return redirect('quiz_list')  # أو صفحة خطأ

    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        if quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.lecture_type = lecture_type
            if lecture_type == 'basic':
                quiz.basic_lecture = lecture
            else:
                quiz.clinical_lecture = lecture
            quiz.save()

            question_formset = QuestionFormSet(request.POST, instance=quiz)
            if question_formset.is_valid():
                questions = question_formset.save()
                for i, question in enumerate(questions):
                    choice_formset = ChoiceFormSet(
                        request.POST,
                        instance=question,
                        prefix=f'choices-{i}'
                    )
                    if choice_formset.is_valid():
                        choice_formset.save()
            return redirect('quiz_list')
    else:
        quiz_form = QuizForm()
        question_formset = QuestionFormSet()
        choice_formsets = [ChoiceFormSet(prefix=f'choices-{i}') for i, f in enumerate(question_formset.forms)]

    return render(request, 'add_lecture_quiz.html', {
        'quiz_form': quiz_form,
        'question_formset': question_formset,
        'choice_formsets': choice_formsets,
        'lecture': lecture
    })

from django.shortcuts import get_object_or_404, render
from .forms import ModuleForm
from .models import Module
@login_required
def edit_module_modal(request, pk):
    module = get_object_or_404(Module, pk=pk)

    if request.method == 'POST':
        form = ModuleForm(request.POST, request.FILES, instance=module)
        if form.is_valid():
            form.save()
            return render(request, 'partials/edit_module_modal.html', {
                'form': form,
                'module': module,
                'success': True
            })
    else:
        form = ModuleForm(instance=module)

    return render(request, 'partials/edit_module_modal.html', {
        'form': form,
        'module': module
    })

from django.shortcuts import render, get_object_or_404
from .models import Module, BasicLecture, ClinicalLecture, Quiz, Certificate, ModuleEnrollment


import json  # <- تأكد من استيراد json

@login_required
def module_manage(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    basic_lectures = module.basiclectures.all()  # related_name = 'basiclectures'
    clinical_lectures = module.clinicallectures.all()  # related_name = 'clinicallectures'
    
    # أضف هذا الجزء لحفظ عناوين الكويز لكل محاضرة كـ JSON
    for lec in basic_lectures:
        quizzes = lec.quizzes.values('id','title')  # فقط id و title
        lec.quiz_titles_json = json.dumps(list(lec.quizzes.values_list('title', flat=True)))

    for lec in clinical_lectures:
        quizzes = lec.quizzes.values('id','title')
        lec.quiz_titles_json = json.dumps(list(lec.quizzes.values_list('title', flat=True)))

    # كل الكويزات
    quizzes = Quiz.objects.filter(
        basic_lecture__in=basic_lectures
    ) | Quiz.objects.filter(
        clinical_lecture__in=clinical_lectures
    )

    # الطلاب المسجلين
    enrollments = ModuleEnrollment.objects.filter(module=module)

    # الشهادات
    certificates = module.certificates.all()

    # قائمة الأنظمة لملأ الـ select
    basic_systems = BasicSystem.objects.all()
    clinical_systems = ClinicalSystem.objects.all()

    context = {
        'module': module,
        'basic_lectures': basic_lectures,
        'clinical_lectures': clinical_lectures,
        'quizzes': quizzes,
        'enrollments': enrollments,
        'certificates': certificates,
        'basic_systems': basic_systems,
        'clinical_systems': clinical_systems,
    }
    return render(request, 'model_details_edit.html', context)

from django.shortcuts import get_object_or_404, redirect
from .models import Module, BasicLecture, ClinicalLecture, Discipline

@login_required
def add_lecture_modal(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        lecture_type = request.POST.get('lecture_type')
        order = request.POST.get('order', 1)

        video_file = request.FILES.get('video_file')  # ← هنا المشكلة الحقيقية

        if module.basic_system:
            discipline_id = request.POST.get('discipline')
            discipline = get_object_or_404(Discipline, id=discipline_id)

            BasicLecture.objects.create(
                module=module,
                title=title,
                description=description,
                lecture_type=lecture_type,
                order=order,
                discipline=discipline,
                instructor=request.user,
                video_file=video_file   # ← إضافة الفيديو
            )

        elif module.clinical_system:
            ClinicalLecture.objects.create(
                module=module,
                title=title,
                description=description,
                lecture_type=lecture_type,
                order=order,
                instructor=request.user,
                video_file=video_file   # ← إضافة الفيديو
            )

    return redirect('lectures:module_manage', module_id=module.id)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import BasicLecture, ClinicalLecture, Module

@csrf_exempt  # أو استخدم @ensure_csrf_cookie مع AJAX
def save_lecture_order(request, module_id):
    if request.method == "POST":
        order = request.POST.getlist('order[]')  # قائمة الـ IDs

        # تحديث ترتيب المحاضرات
        for index, lec_id in enumerate(order, start=1):
            # حاول إيجاد المحاضرة في Basic وClinical
            try:
                lec = BasicLecture.objects.get(id=lec_id, module_id=module_id)
            except BasicLecture.DoesNotExist:
                try:
                    lec = ClinicalLecture.objects.get(id=lec_id, module_id=module_id)
                except ClinicalLecture.DoesNotExist:
                    continue  # إذا لم توجد المحاضرة تجاهلها

            lec.order = index  # تأكد من وجود حقل order في النموذج
            lec.save()

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

# lectures/views.py
from django.shortcuts import get_object_or_404, render
from .models import BasicLecture, ClinicalLecture

def lecture_detail_modal(request, type, lecture_id):
    if type == "basic":
        lecture = get_object_or_404(BasicLecture, id=lecture_id)
        template = "lectures/modals/basic_lecture_detail.html"
    else:
        lecture = get_object_or_404(ClinicalLecture, id=lecture_id)
        template = "lectures/modals/clinical_lecture_detail.html"

    return render(request, template, {
        "lecture": lecture
    })
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

@login_required
@require_POST
def delete_lecture_ajax(request, lecture_type, lecture_id):
    # تحقق ونمسح المحاضرة
    if lecture_type == 'basic':
        lec = get_object_or_404(BasicLecture, id=lecture_id)
    else:
        lec = get_object_or_404(ClinicalLecture, id=lecture_id)

    # امنع الحذف لو مش المعلم المالك
    if lec.instructor != request.user:
        return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)

    lec.delete()
    return JsonResponse({'success': True, 'message': 'Lecture deleted'})

@login_required
def edit_lecture_ajax(request, lecture_type, lecture_id):
    # يسمح GET لإرجاع HTML للنموذج (للمودال) و POST لتحديث البيانات
    if lecture_type == 'basic':
        lecture = get_object_or_404(BasicLecture, id=lecture_id)
        is_basic = True
    else:
        lecture = get_object_or_404(ClinicalLecture, id=lecture_id)
        is_basic = False

    if lecture.instructor != request.user:
        return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)

    if request.method == 'GET':
        # نرجع JSON بسيط لملء الفورم في المودال
        data = {
            'id': lecture.id,
            'title': lecture.title,
            'description': lecture.description or '',
            'order': lecture.order,
            'lecture_type': lecture.lecture_type,
            # للـ basic: discipline id
            'discipline_id': getattr(lecture, 'discipline_id', None),
        }
        return JsonResponse({'success': True, 'lecture': data})

    # POST -> update
    title = request.POST.get('title')
    description = request.POST.get('description')
    order = request.POST.get('order') or lecture.order
    lecture_type_field = request.POST.get('lecture_type')

    # تحديث الحقول العامة
    lecture.title = title or lecture.title
    lecture.description = description
    try:
        lecture.order = int(order)
    except Exception:
        pass

    # handle file (video)
    if 'video_file' in request.FILES:
        lecture.video_file = request.FILES['video_file']

    # اذا كان basic وحصلنا discipline
    if is_basic:
        disc_id = request.POST.get('discipline')
        if disc_id:
            from .models import Discipline
            try:
                lecture.discipline = Discipline.objects.get(id=disc_id)
            except Discipline.DoesNotExist:
                pass

    lecture.save()
    return JsonResponse({'success': True, 'message': 'Lecture updated', 'lecture_id': lecture.id})
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from lectures.models import BasicLecture, ClinicalLecture, Quiz

@require_POST
def create_quiz(request):
    lecture_id = request.POST.get("lecture_id")
    title = request.POST.get("title")

    # Try basic lecture first
    lecture = None
    lecture_type = None

    try:
        lecture = BasicLecture.objects.get(id=lecture_id)
        lecture_type = "basic"
    except BasicLecture.DoesNotExist:
        try:
            lecture = ClinicalLecture.objects.get(id=lecture_id)
            lecture_type = "clinical"
        except ClinicalLecture.DoesNotExist:
            return JsonResponse({"success": False, "error": "Lecture not found"})

    # Create Quiz based on lecture type
    if lecture_type == "basic":
        quiz = Quiz.objects.create(
            lecture_type="basic",
            basic_lecture=lecture,
            title=title
        )
    else:
        quiz = Quiz.objects.create(
            lecture_type="clinical",
            clinical_lecture=lecture,
            title=title
        )

    return JsonResponse({"success": True, "quiz_id": quiz.id})

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from lectures.models import Quiz, Question, Choice

@require_POST
def create_question(request):
    quiz_id = request.POST.get("quiz_id")
    text = request.POST.get("text")
    correct = request.POST.get("correct")  # رقم الاختيار الصحيح (1–4)

    quiz = Quiz.objects.get(id=quiz_id)

    # Create question
    q = Question.objects.create(
        quiz=quiz,
        text=text
    )

    # Options
    options = [
        request.POST.get("option1"),
        request.POST.get("option2"),
        request.POST.get("option3"),
        request.POST.get("option4"),
    ]

    # Create choices
    for i, option_text in enumerate(options, start=1):
        Choice.objects.create(
            question=q,
            text=option_text,
            is_correct=(str(i) == str(correct))
        )

    return JsonResponse({
        "success": True,
        "question_text": q.text
    })
from django.http import JsonResponse
from .models import Quiz
def quiz_details(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    
    questions = []
    for q in quiz.questions.all():
        choices = []
        for c in q.choices.all():
            choices.append({
                "id": c.id,
                "text": c.text,
                "is_correct": c.is_correct,
            })

        questions.append({
            "id": q.id,
            "text": q.text,
            "choices": choices
        })

    return JsonResponse({
        "success": True,
        "quiz": {
            "id": quiz.id,
            "title": quiz.title,
            "questions": questions
        }
    })
def quiz_delete(request, quiz_id):
    quiz = Quiz.objects.filter(id=quiz_id).first()
    if not quiz:
        return JsonResponse({"success": False, "error": "Quiz not found"})

    quiz.delete()
    return JsonResponse({"success": True})

def question_edit(request, question_id):
    question = Question.objects.filter(id=question_id).first()
    if not question:
        return JsonResponse({"success": False, "error": "Question not found"})

    new_text = request.POST.get("text")
    if new_text:
        question.text = new_text
        question.save()

    return JsonResponse({"success": True})
def question_delete(request, question_id):
    question = Question.objects.filter(id=question_id).first()
    if not question:
        return JsonResponse({"success": False, "error": "Question not found"})

    question.delete()
    return JsonResponse({"success": True})
