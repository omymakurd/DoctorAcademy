import stripe
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404, render
from courses.models import Course
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

def process_checkout(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        if payment_method == "stripe":
            # إنشاء Payment جديد بحالة pending
            payment = Payment.objects.create(
                student=request.user,
                course=course,
                amount=course.price,
                method='card',
                status='pending'
            )

            # إنشاء Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'egp',
                        'product_data': {
                            'name': course.title,
                        },
                        'unit_amount': int(course.price * 100),  # بالسنت
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(f'/payments/courses/success/?payment_id={payment.id}'),
                cancel_url=request.build_absolute_uri(f'/payments/courses/cancel/?payment_id={payment.id}'),
            )

            # حفظ transaction_id من Stripe
            payment.transaction_id = checkout_session.id
            payment.save()

            return redirect(checkout_session.url)

    return redirect('courses:course_detail', course_id=course.id)


def payment_success(request):
    payment_id = request.GET.get('payment_id')
    payment = get_object_or_404(Payment, id=payment_id)

    session = stripe.checkout.Session.retrieve(payment.transaction_id)
    if session.payment_status == 'paid':
        payment.status = 'completed'
        payment.save()

    return render(request, 'success.html', {'payment': payment})


def payment_cancel(request):
    payment_id = request.GET.get('payment_id')
    payment = get_object_or_404(Payment, id=payment_id)
    payment.status = 'failed'
    payment.save()
    return render(request, 'cancel.html', {'payment': payment})
