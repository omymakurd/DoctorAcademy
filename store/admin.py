from django.contrib import admin
from .models import Product, Order, OrderItem

# ========================
# Product
# ========================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)

# ========================
# OrderItem Inline
# ========================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity')
    can_delete = False

# ========================
# Order
# ========================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('student', 'get_products', 'total_amount', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('student__username', 'products__name')
    readonly_fields = ('total_amount', 'created_at', 'updated_at')
    inlines = [OrderItemInline]

    def get_products(self, obj):
        return ", ".join([f"{item.product.name} (x{item.quantity})" for item in obj.orderitem_set.all()])
    get_products.short_description = "Products"
