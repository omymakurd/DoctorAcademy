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

    return redirect('view_cart')


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
@login_required
def checkout_store(request):
    order = Order.objects.filter(student=request.user, status='pending').first()

    if not order or not order.orderitem_set.exists():
        return redirect('store_home')

    return render(request, 'checkout_store.html', {'order': order})