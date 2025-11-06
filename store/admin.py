from django.contrib import admin
from .models import Product, ProductImage, Order, OrderItem


# ========================
# Inline: صور إضافية للمنتج
# ========================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image']
    max_num = 8


# ========================
# Product
# ========================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount', 'final_price_display', 'stock', 'seller', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'seller')
    inlines = [ProductImageInline]

    def final_price_display(self, obj):
        return obj.final_price()
    final_price_display.short_description = "Final Price"


# ========================
# Inline: OrderItems داخل الطلب
# ========================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'subtotal_display')
    can_delete = False

    def subtotal_display(self, obj):
        return obj.subtotal()
    subtotal_display.short_description = "Subtotal"


# ========================
# Order
# ========================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'total_amount', 'status', 'payment', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('student__username', 'orderitem__product__name')
    readonly_fields = ('total_amount', 'created_at', 'updated_at')
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('orderitem_set__product')
