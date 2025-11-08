import stripe
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from courses.models import Course
from lectures.models import BasicLecture, ClinicalLecture, Module, ModuleEnrollment
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

# -------------------------
# Checkout لـ Course
# -------------------------
@login_required
def process_checkout(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        payment = Payment.objects.create(
            student=request.user,
            course=course,
            amount=course.price,
            method='card',
            status='pending'
        )

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'egp',
                    'product_data': {'name': course.title},
                    'unit_amount': int(course.price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(f'/payments/courses/success/?payment_id={payment.id}'),
            cancel_url=request.build_absolute_uri(f'/payments/courses/cancel/?payment_id={payment.id}'),
        )

        payment.transaction_id = checkout_session.id
        payment.save()
        return redirect(checkout_session.url)

    return redirect('courses:course_detail', course_id=course.id)


# -------------------------
# Checkout لمحاضرة Basic
# -------------------------
@login_required
def process_checkout_basic(request, lecture_id):
    lecture = get_object_or_404(BasicLecture, id=lecture_id)

    if request.method == "POST":
        payment = Payment.objects.create(
            student=request.user,
            lecture_basic=lecture,
            amount=lecture.price,
            method='card',
            status='pending'
        )

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'egp',
                    'product_data': {'name': lecture.title},
                    'unit_amount': int(lecture.price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(f'/payments/courses/success/?payment_id={payment.id}'),
            cancel_url=request.build_absolute_uri(f'/payments/courses/cancel/?payment_id={payment.id}'),
        )

        payment.transaction_id = checkout_session.id
        payment.save()
        return redirect(checkout_session.url)

    return redirect('lectures:basic_detail', lecture_id)


# -------------------------
# Checkout لمحاضرة Clinical
# -------------------------
@login_required
def process_checkout_clinical(request, lecture_id):
    lecture = get_object_or_404(ClinicalLecture, id=lecture_id)

    if request.method == "POST":
        payment = Payment.objects.create(
            student=request.user,
            lecture_clinical=lecture,
            amount=lecture.price,
            method='card',
            status='pending'
        )

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'egp',
                    'product_data': {'name': lecture.title},
                    'unit_amount': int(lecture.price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(f'/payments/courses/success/?payment_id={payment.id}'),
            cancel_url=request.build_absolute_uri(f'/payments/courses/cancel/?payment_id={payment.id}'),
        )

        payment.transaction_id = checkout_session.id
        payment.save()
        return redirect(checkout_session.url)

    return redirect('lectures:clinical_detail', lecture_id)


# -------------------------
# Checkout لموديول
# -------------------------
@login_required
def process_checkout_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    if ModuleEnrollment.objects.filter(student=request.user, module=module).exists():
        return redirect('lectures:module_detail', module_id=module.id)

    payment = Payment.objects.create(
    student=request.user,
    module=module,
    amount=module.price,
    method='card',
    status='pending'
)


    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f"{module.title} Module ({'Basic' if module.basic_system else 'Clinical'})",
                },
                'unit_amount': int(module.price * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(f'/payments/courses/success/?payment_id={payment.id}'),
        cancel_url=request.build_absolute_uri(f'/payments/courses/cancel/?payment_id={payment.id}'),
    )

    payment.transaction_id = checkout_session.id
    payment.save()
    return redirect(checkout_session.url)


# -------------------------
# صفحة نجاح الدفع وإضافة الطالب
# -------------------------
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from courses.models import Course, Enrollment, CourseUnit
from lectures.models import BasicLecture, ClinicalLecture, Module, ModuleEnrollment
from .models import Payment
import stripe
from django.conf import settings
from django.urls import reverse

@login_required
def payment_success(request):
    payment_id = request.GET.get('payment_id')
    start_url = '/'  # رابط افتراضي إذا ما فيه كورس

    if not payment_id:
        return render(request, 'success.html', {'start_url': start_url})

    payment = get_object_or_404(Payment, id=payment_id)

    # تحقق من حالة الدفع عبر Stripe
    session = stripe.checkout.Session.retrieve(payment.transaction_id)
    if session.payment_status == 'paid' and payment.status != 'completed':
        payment.status = 'completed'
        payment.save()

        # ===============================
        # إضافة الطالب للكورس
        # ===============================
        if payment.course:
            enrollment, created = Enrollment.objects.get_or_create(
                student=request.user,
                course=payment.course,
                defaults={'paid': True}
            )
            if not created:
                enrollment.paid = True
                enrollment.save()

            # إضافة الطالب لكل وحدات الكورس (ModuleEnrollment)
            for unit in payment.course.units.all():
                ModuleEnrollment.objects.get_or_create(
                    student=request.user,
                    module=unit,
                    purchased_price=unit.price if hasattr(unit, 'price') else 0
                )

        # ===============================
        # إضافة الطالب لمحاضرة Basic
        # ===============================
        if payment.lecture_basic:
            ModuleEnrollment.objects.get_or_create(
                student=request.user,
                module=payment.lecture_basic.module,
                purchased_price=payment.lecture_basic.price
            )

        # ===============================
        # إضافة الطالب لمحاضرة Clinical
        # ===============================
        if payment.lecture_clinical:
            ModuleEnrollment.objects.get_or_create(
                student=request.user,
                module=payment.lecture_clinical.module,
                purchased_price=payment.lecture_clinical.price
            )

        # ===============================
        # إضافة الطالب لأي Module منفصل
        # ===============================
        if payment.module:
            ModuleEnrollment.objects.get_or_create(
                student=request.user,
                module=payment.module,
                purchased_price=payment.module.price
            )

        # بعد كل شيء، إذا فيه كورس، ابدأ الكورس مباشرة
        if payment.course:
            start_url = reverse('courses:learn_course', args=[payment.course.id])

    return render(request, 'success.html', {'payment': payment, 'start_url': start_url})
# -------------------------
# صفحة إلغاء الدفع
# -------------------------
@login_required
def payment_cancel(request):
    payment_id = request.GET.get('payment_id')
    payment = get_object_or_404(Payment, id=payment_id)
    payment.status = 'failed'
    payment.save()
    return render(request, 'cancel.html', {'payment': payment})
