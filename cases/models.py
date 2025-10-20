from django.db import models
from users.models import User
from lectures.models import BasicLecture, ClinicalLecture

# اختيارات الأقسام لكل discipline
DISCIPLINE_SECTIONS = [
    ('anatomy','Anatomy'),
    ('embryology','Embryology'),
    ('histology','Histology'),
    ('physiology','Physiology'),
    ('pathology','Pathology'),
    ('pharmacology','Pharmacology'),
]

class CaseStudy(models.Model):
    title = models.CharField(max_length=255)
    symptoms = models.TextField()
    analysis = models.TextField()
    
    # مين أنشأ الكيس ستادي
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cases_created')
    
    # تختار القسم (Anatomy, Embryology …) لكل case
    discipline_section = models.CharField(max_length=20, choices=DISCIPLINE_SECTIONS,default='anatomy')
    
    # الربط مع المحاضرات المناسبة
    related_basic_lectures = models.ManyToManyField(BasicLecture, related_name='cases_basic', blank=True)
    related_clinical_lectures = models.ManyToManyField(ClinicalLecture, related_name='cases_clinical', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_discipline_section_display()})"
