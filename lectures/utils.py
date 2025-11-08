# lectures/utils.py
from django.shortcuts import get_object_or_404
from .models import BasicLecture, ClinicalLecture, Module
from payments.models import Payment

def user_has_paid_for_basic_lecture(user, lecture: BasicLecture) -> bool:
    if not user.is_authenticated:
        return False
    # lecture.price may not exist on BasicLecture model; if not, treat as free (modify if needed)
    # هنا نتحقق من وجود سجل دفع مكتمل مرتبط بهذه المحاضرة
    return Payment.objects.filter(student=user, lecture_basic=lecture, status='completed').exists()

def user_has_paid_for_clinical_lecture(user, lecture: ClinicalLecture) -> bool:
    if not user.is_authenticated:
        return False
    return Payment.objects.filter(student=user, lecture_clinical=lecture, status='completed').exists()

def user_has_access_to_lecture(user, lecture):
    """
    general helper: accepts either BasicLecture or ClinicalLecture instance
    """
    from django.db.models import Model
    if not hasattr(lecture, '__class__'):
        return False
    cls_name = lecture.__class__.__name__.lower()
    if cls_name == 'basiclecture':
        return user_has_paid_for_basic_lecture(user, lecture)
    elif cls_name == 'clinicallecture':
        return user_has_paid_for_clinical_lecture(user, lecture)
    return False

def module_user_is_enrolled(user, module: Module) -> bool:
    return module.enrollments.filter(student=user).exists()
