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


@login_required
def add_lecture(request, module_id):
    if request.method == 'POST':
        # تحقق أي نوع Module: Basic أو Clinical
        module = Module.objects.get(id=module_id)
        if module.basic_system:
            form = BasicLectureForm(request.POST, request.FILES)
        else:
            form = ClinicalLectureForm(request.POST, request.FILES)

        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.module = module
            lecture.instructor = request.user
            lecture.save()
            return JsonResponse({'success': True, 'lecture_id': lecture.id})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'errors': 'Invalid request'})


from .models import BasicLecture, ClinicalLecture, Quiz

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
    return render(request, 'add_module_wizerd.html', {
        'module_form': module_form,
        'lecture_form': lecture_form
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