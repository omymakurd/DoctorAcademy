from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, OrderItem
from django.contrib.auth.decorators import login_required

def store_home(request):
    products = Product.objects.all()
    return render(request, 'store.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    order, _ = Order.objects.get_or_create(student=request.user, status='pending')

    item, created = OrderItem.objects.get_or_create(order=order, product=product)
    item.quantity += quantity
    item.save()

    order.calculate_total()

    return redirect('store:view_cart')


@login_required
def view_cart(request):
    order = Order.objects.filter(student=request.user, status='pending').first()
    return render(request, 'cart.html', {'order': order})
from django.contrib.auth.decorators import login_required

@login_required
def update_quantity(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__student=request.user, order__status='pending')
    
    action = request.POST.get('action')

    if action == "increase":
        item.quantity += 1
    elif action == "decrease" and item.quantity > 1:
        item.quantity -= 1

    item.save()
    item.order.calculate_total()
    return redirect('view_cart')


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__student=request.user, order__status='pending')
    order = item.order
    item.delete()
    order.calculate_total()
    return redirect('view_cart')



from django.shortcuts import redirect, get_object_or_404
from store.models import Order  # افترض أن عندك موديل Order للـ Cart
from payments.models import Payment
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout_store_direct(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # إنشاء Payment مرتبط بالـ order
    payment = Payment.objects.create(
        student=request.user,
        amount=order.total_amount,
        method='card',
        status='pending'
    )

    # إنشاء Stripe Checkout Session
    line_items = []
    for item in order.orderitem_set.all():  # ✅ هذا صحيح حسب المودل الحالي
        line_items.append({
        'price_data': {
            'currency': 'usd',
            'product_data': {'name': item.product.name},
            'unit_amount': int(item.product.final_price() * 100),
        },
        'quantity': item.quantity,
    })


    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri(f'/payments/courses/success/?payment_id={payment.id}'),
        cancel_url=request.build_absolute_uri(f'/payments/courses/cancel/?payment_id={payment.id}'),
    )

    payment.transaction_id = checkout_session.id
    payment.save()

    return redirect(checkout_session.url)
