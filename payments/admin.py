from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'get_item',
        'amount',
        'method',
        'status',
        'instructor_amount',
        'provider_amount',
        'platform_amount',
        'transaction_id',
        'created_at'
    )
    list_filter = ('status', 'method', 'created_at')
    search_fields = (
        'student__username',
        'transaction_id',
        'lecture_basic__title',
        'lecture_clinical__title',
        'course__title'
    )
    readonly_fields = (
        'instructor_amount',
        'provider_amount',
        'platform_amount',
        'created_at',
        'updated_at'
    )

    def get_item(self, obj):
        """عرض اسم المحاضرة أو الدورة المدفوعة"""
        if obj.lecture_basic:
            return f"Basic Lecture: {obj.lecture_basic.title}"
        elif obj.lecture_clinical:
            return f"Clinical Lecture: {obj.lecture_clinical.title}"
        elif obj.course:
            return f"Course: {obj.course.title}"
        return "-"
    get_item.short_description = "Item"
