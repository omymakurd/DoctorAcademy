from django.db import models
from users.models import User


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    price = models.DecimalField(max_digits=8, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # نسبة الخصم %

    stock = models.PositiveIntegerField(default=0)

    image = models.ImageField(upload_to='store/products/', blank=True, null=True)

    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # اختياري
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def final_price(self):
        """سعر المنتج بعد الخصم"""
        if self.discount > 0:
            return self.price - (self.price * (self.discount / 100))
        return self.price

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """صور إضافية للمنتج"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="store/products/gallery/")

    def __str__(self):
        return f"Image for {self.product.name}"


class Order(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, through='OrderItem')

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status_choices = [
        ('pending', 'Pending'),      # السلة Cart
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='pending')

    payment = models.OneToOneField('payments.Payment', on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total(self):
        """حساب إجمالي الطلب"""
        total = sum(item.subtotal() for item in self.orderitem_set.all())
        self.total_amount = total
        self.save()

    def __str__(self):
        return f"Order #{self.id} - {self.student.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        """سعر العنصر داخل الطلب"""
        return self.product.final_price() * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
