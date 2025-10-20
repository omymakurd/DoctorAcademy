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

@login_required
def instructor_dashboard(request):
    user = request.user

    # عدد الدورات والمحاضرات والطلاب والكيس ستادي
    courses_count = Course.objects.filter(provider=user).count()
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
        'courses_count': courses_count,
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


@login_required
def add_basic_lecture(request):
    if request.user.role != "instructor":
        return redirect('home')

    if request.method == 'POST':
        form = BasicLectureForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.instructor = request.user
            lecture.save()
            return redirect('instructor_dashboard')
    else:
        form = BasicLectureForm(user=request.user)

    return render(request, 'add_basic_lecture.html', {'form': form})


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