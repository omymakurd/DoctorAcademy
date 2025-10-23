from django.db import models
from users.models import User
from lectures.models import BasicLecture, ClinicalLecture

class CaseStudy(models.Model):
    title = models.CharField(max_length=255)
    symptoms = models.TextField(blank=True)
    analysis = models.TextField(blank=True)
    discipline = models.CharField(
        max_length=50,
        choices=[
            ('anatomy','Anatomy'),
            ('embryology','Embryology'),
            ('histology','Histology'),
            ('physiology','Physiology'),
            ('pathology','Pathology'),
            ('pharmacology','Pharmacology'),
        ],
        default='anatomy'
    )

    # ربط المحاضرات
    basic_lecture = models.ForeignKey(
        'lectures.BasicLecture', on_delete=models.CASCADE, 
        null=True, blank=True, related_name='case_studies'
    )
    clinical_lecture = models.ForeignKey(
        'lectures.ClinicalLecture', on_delete=models.CASCADE, 
        null=True, blank=True, related_name='case_studies'
    )

    # خيارات الوسائط
    video = models.FileField(
        upload_to='case_studies/videos/', null=True, blank=True,
        help_text="Upload a video file"
    )
    video_url = models.URLField(
        null=True, blank=True,
        help_text="External or YouTube video link"
    )
    attachment = models.FileField(
        upload_to='case_studies/files/', null=True, blank=True,
        help_text="Upload supporting file (PDF, image, etc.)"
    )

    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='cases_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.discipline})"

    def get_media_type(self):
        """Helper: يحدد نوع الوسائط"""
        if self.video:
            return "file_video"
        elif self.video_url:
            return "external_video"
        elif self.attachment:
            return "file_attachment"
        return "text_only"
