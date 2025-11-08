from django.db import models
from decimal import Decimal
from users.models import User
from courses.models import Course
from lectures.models import BasicLecture, ClinicalLecture
from lectures.models import Module
class Payment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    lecture_basic = models.ForeignKey(BasicLecture, on_delete=models.CASCADE, null=True, blank=True)
    lecture_clinical = models.ForeignKey(ClinicalLecture, on_delete=models.CASCADE, null=True, blank=True)
    
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    method = models.CharField(
        max_length=20,
        choices=[('card','Credit/Debit Card'),('paypal','Paypal'),('bank','Bank Transfer')]
    )
    status = models.CharField(
        max_length=20,
        choices=[('pending','Pending'),('completed','Completed'),('failed','Failed')],
        default='pending'
    )
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, null=True, blank=True)
    # توزيع الأرباح
    instructor_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    provider_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    platform_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        عند الحفظ، يحسب تلقائيًا:
        - أرباح المحاضر
        - أرباح المزود
        - أرباح المنصة
        """
        # تحديد نسبة أرباح المحاضر والمزود
        if self.lecture_basic:
            instructor_share = getattr(self.lecture_basic.instructor.instructor_profile, 'default_profit_share', 0)
            provider_share = getattr(getattr(self.lecture_basic.instructor, 'provider_profile', None), 'profit_share', 0)
        elif self.lecture_clinical:
            instructor_share = getattr(self.lecture_clinical.instructor.instructor_profile, 'default_profit_share', 0)
            provider_share = getattr(getattr(self.lecture_clinical.instructor, 'provider_profile', None), 'profit_share', 0)
        elif self.course and self.course.provider:
            instructor_share = 0
            provider_share = getattr(getattr(self.course.provider, 'provider_profile', None), 'profit_share', 0)
        elif self.module:
            instructor_share = getattr(self.module.instructor.instructor_profile, 'default_profit_share', 0)
            provider_share = getattr(getattr(self.module.instructor, 'provider_profile', None), 'profit_share', 0)

        else:
            instructor_share = 0
            provider_share = 0

        # تحويل النسب إلى Decimal قبل الحساب
        instructor_share_decimal = Decimal(instructor_share) / Decimal('100')
        provider_share_decimal = Decimal(provider_share) / Decimal('100')

        # حساب الأرباح
        self.instructor_amount = (self.amount * instructor_share_decimal).quantize(Decimal('0.01'))
        self.provider_amount = (self.amount * provider_share_decimal).quantize(Decimal('0.01'))
        self.platform_amount = (self.amount - (self.instructor_amount + self.provider_amount)).quantize(Decimal('0.01'))

        super().save(*args, **kwargs)
