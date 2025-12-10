
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import CaseStudyNew
from .forms import CaseStudyNewForm

# ======= List Cases =======
@login_required
def case_list(request):
    cases = CaseStudyNew.objects.all().order_by('-created_at')
    return render(request, "case_list.html", {"cases": cases})

# ======= Create Case =======
from django.urls import reverse
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .models import CaseStudyNew
from .forms import CaseStudyNewForm
from .zoom_utils import create_zoom_meeting
from datetime import datetime, timedelta


@login_required
def case_create(request):
    if request.method == "POST":
        form = CaseStudyNewForm(request.POST, request.FILES)
        if form.is_valid():
            new_case = form.save(commit=False)
            new_case.created_by = request.user
            new_case.approval_status = "pending"
            start_dt = datetime.combine(
            form.cleaned_data["session_date"],
            form.cleaned_data["session_time"]
        )

            meeting = create_zoom_meeting(
            topic=form.cleaned_data["title"],
            start_time=start_dt
)

            new_case.zoom_meeting_id = meeting["id"]
            new_case.zoom_meeting_password = meeting["password"]

            new_case.save()

            

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'case': {
                        'id': new_case.id,
                        'title': new_case.title,
                        'discipline': new_case.discipline,
                        'target_level': new_case.target_level,
                        'session_date': new_case.session_date.strftime("%Y-%m-%d") if new_case.session_date else "",
                        'approval_status': new_case.approval_status,
                        'edit_url': reverse('cases_new:edit', args=[new_case.id]),
                        'detail_url': reverse('cases_new:detail', args=[new_case.id]),
                    }
                })
            return redirect('cases_new:list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html_form = render_to_string('case_form.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'html_form': html_form})
    else:
        form = CaseStudyNewForm()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html_form = render_to_string('case_form.html', {'form': form}, request=request)
            return JsonResponse({'success': False, 'html_form': html_form})

    return render(request, "case_form.html", {"form": form, "action": "Create"})


from django.http import JsonResponse, HttpResponse
from django.urls import reverse
# ======= Edit Case =======

@login_required
def case_edit(request, pk):
    case = get_object_or_404(CaseStudyNew, pk=pk)

    if request.method == "POST":
        form = CaseStudyNewForm(request.POST, request.FILES, instance=case)
        if form.is_valid():
            form.save()
            case.refresh_from_db()  # ← مهم جداً

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'case': {
                        'id': case.id,
                        'title': case.title,
                        'discipline': case.discipline,
                        'target_level': case.target_level,
                        'session_date': case.session_date,
                        'approval_status': case.approval_status,
                        'edit_url': reverse('cases_new:edit', args=[case.id]),
                        'detail_url': reverse('cases_new:detail', args=[case.id]),
                    }
                })
            else:
                return redirect('cases_new:list')

        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html_form = render_to_string("case_form.html", {"form": form, "action": "Edit"}, request=request)
                return JsonResponse({"success": False, "html_form": html_form})

    else:
        form = CaseStudyNewForm(instance=case)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html_form = render_to_string("case_form.html", {"form": form, "action": "Edit"}, request=request)
            return JsonResponse({"success": False, "html_form": html_form})

        return render(request, "case_form.html", {"form": form, "action": "Edit"})


# ======= View Case Details =======
@login_required
def case_detail(request, pk):
    case = get_object_or_404(CaseStudyNew, pk=pk)
    html = render_to_string('case_detail.html', {'case': case}, request=request)
    return HttpResponse(html)


@login_required
def case_delete(request, pk):
    case = get_object_or_404(CaseStudyNew, pk=pk, created_by=request.user)
    if request.method == 'POST':
        case.delete()
        return JsonResponse({'success': True})
    # إذا لم يكن POST، نرجع JSON أيضاً
    return JsonResponse({'success': False})


# cases_new/views.py

from django.shortcuts import render
from .models import CaseStudyNew
from django.db.models import Q

def student_case_list(request):
    # جلب فقط الحالات الموافَق عليها
    cases = CaseStudyNew.objects.filter(approval_status="approved")

    # فلترة حسب التخصص
    discipline = request.GET.get("discipline")
    if discipline and discipline != "all":
        cases = cases.filter(discipline=discipline)

    # بحث
    search = request.GET.get("search")
    if search:
        cases = cases.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    return render(request, "student_case_list.html", {
        "cases": cases,
        "selected_discipline": discipline,
    })
def student_case_detail(request, pk):
    case = get_object_or_404(
        CaseStudyNew,
        pk=pk,
        approval_status="approved"  # يظهر فقط المعتمدة
    )

    return render(request, "student_case_detail.html", {
        "case": case
    })


# views.py (جديد)
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import CaseStudyNew
from .zoom_utils import generate_zoom_signature
from django.conf import settings

@login_required
def case_detail(request, pk):
    case = get_object_or_404(CaseStudyNew, pk=pk, approval_status="approved")

    # --- Authorization: تأكد أن المستخدم مُخوّل
    # قاعدة: creator (المحاضر) أو مستخدم مسجّل في الدورة يمكنه الدخول.
    # هنا تحتاج تعديل شرط "is_registered" حسب منطق مشروعك (مثال مبسط):
    is_creator = (case.created_by == request.user)
    is_registered_student = True  # <-- عدل هذا: مثلاً تحقق من تسجيل المستخدم في الدورة/الدرس

    if not (is_creator or is_registered_student):
        # منع الوصول لمن ليس لديهم صلاحية
        raise Http404("You are not authorized to view this session.")

    # دور Zoom: المحاضر role=1، الباقي role=0
    role = 1 if is_creator else 0

    meeting_number = str(case.zoom_meeting_id)
    zoom_signature = generate_zoom_signature(meeting_number, role)
    zoom_sdk_key = settings.ZOOM_SDK_KEY

    # user_name يجب أن يأتي من السيرفر (غير قابل للتعديل من client)
    user_name = f"{request.user.first_name} {request.user.last_name}" if (request.user.first_name or request.user.last_name) else request.user.username

    # مرّر بيانات الـ Zoom بأمان للقالب
    context = {
        "case": case,
        "zoom_sdk_key": zoom_sdk_key,
        "zoom_signature": zoom_signature,
        "meeting_number": meeting_number,
        "zoom_role": role,
        "zoom_user_name": user_name,
    }
    return render(request, "student_case_detail.html", context)
from django.http import JsonResponse
@login_required
def zoom_signature_endpoint(request, pk):
    case = get_object_or_404(CaseStudyNew, pk=pk, approval_status="approved")
    # authorization checks...
    role = 1 if case.created_by == request.user else 0
    signature = generate_zoom_signature(str(case.zoom_meeting_id), role)
    return JsonResponse({
        "signature": signature,
        "sdkKey": settings.ZOOM_SDK_KEY,
        "meetingNumber": str(case.zoom_meeting_id),
        "role": role,
        "userName": f"{request.user.first_name} {request.user.last_name}" or request.user.username
    })