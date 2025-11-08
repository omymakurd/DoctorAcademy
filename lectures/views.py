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

@login_required
def instructor_dashboard(request):
    user = request.user

    # عدد الدورات والمحاضرات والطلاب والكيس ستادي
    
    lectures_count = BasicLecture.objects.filter(instructor=user).count() + ClinicalLecture.objects.filter(instructor=user).count()
    students_count = User.objects.filter(lecture_progress__basic_lecture__in=BasicLecture.objects.filter(instructor=user)).distinct().count() + \
                     User.objects.filter(lecture_progress__clinical_lecture__in=ClinicalLecture.objects.filter(instructor=user)).distinct().count()
    cases_count = CaseStudy.objects.filter(created_by=user).count()

    # بيانات Recent Activity (آخر 10 تسجيلات تقدم للطلاب على محاضرات هذا المحاضر)
    recent_progress = LectureProgress.objects.filter(
        basic_lecture__in=BasicLecture.objects.filter(instructor=user)
    ).order_by('-completed_at')[:10]

    # مثال بيانات للCharts
    lecture_labels = [lecture.title for lecture in BasicLecture.objects.filter(instructor=user)]
    lecture_data = [LectureProgress.objects.filter(basic_lecture=lecture, status='completed').count() for lecture in BasicLecture.objects.filter(instructor=user)]

    student_labels = [student.username for student in User.objects.filter(lecture_progress__basic_lecture__in=BasicLecture.objects.filter(instructor=user)).distinct()]
    student_data = [LectureProgress.objects.filter(student__username=username, status='completed').count() for username in student_labels]

    context = {
       
        'lectures_count': lectures_count,
        'students_count': students_count,
        'cases_count': cases_count,
        'recent_progress': recent_progress,
        'lecture_labels': lecture_labels,
        'lecture_data': lecture_data,
        'student_labels': student_labels,
        'student_data': student_data,
        'primary_color': '#0D47A1',
        'accent_color': '#FFA000',
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
def add_clinical_lecture(request):
    if not request.user.is_instructor:
        return redirect('home')

    if request.method == 'POST':
        form = ClinicalLectureForm(request.POST, user=request.user)
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.instructor = request.user
            lecture.save()
            return redirect('instructor_dashboard')
    else:
        form = ClinicalLectureForm(user=request.user)

    return render(request, 'add_clinical_lecture.html', {'form': form})

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

    basic_systems = BasicSystem.objects.all()
    clinical_systems = ClinicalSystem.objects.all()

    return render(request, "module_list.html", {
        "modules": modules,
        "basic_systems": basic_systems,
        "clinical_systems": clinical_systems,
    })


from django.shortcuts import render, get_object_or_404
from .models import Module

def module_detail(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    user_enrolled = False

    if request.user.is_authenticated:
        user_enrolled = request.user.module_enrollments.filter(module=module).exists()

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
    module = get_object_or_404(Module, id=module_id, instructor=request.user)

    if request.method == "POST":
        form = ModuleForm(request.POST, request.FILES, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, "Module updated successfully ✅")
            return redirect('lectures:my_lectures')
    else:
        form = ModuleForm(instance=module)

    return render(request, "edit_module.html", {"form": form, "module": module})

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

@login_required
def add_clinical_lecture(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        video_url = request.POST.get("video_url")

        if not title or not video_url:
            messages.error(request, "Title and Video URL are required.")
            return redirect("add_clinical_lecture", module_id=module.id)

        lecture = ClinicalLecture.objects.create(
            module=module,
            title=title,
            description=description,
            video_url=video_url
        )

        messages.success(request, "Clinical Lecture added successfully.")
        return redirect("module_details", module_id=module.id)

    return render(request, "lectures/add_clinical_lecture.html", {"module": module})
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Module, BasicLecture, ClinicalLecture, LectureReview

@login_required
def module_learning_view(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    # التأكد من تسجيل الطالب في الموديول
    if not module.enrollments.filter(student=request.user).exists():
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You are not enrolled in this module.")

    # جلب المحاضرات بدون الاعتماد على العلاقة العكسية
    basic_lectures = list(BasicLecture.objects.filter(module=module))
    clinical_lectures = list(ClinicalLecture.objects.filter(module=module))
    all_lectures = basic_lectures + clinical_lectures

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
