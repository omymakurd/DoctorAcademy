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

# cases/models_new.py


from django.db import models
from users.models import User


class CaseStudyNew(models.Model):
    # المعلومات الأساسية
    title = models.CharField(max_length=255)
    discipline = models.CharField(
        max_length=50,
        choices=[
            ('internal', 'Internal Medicine'),
            ('surgery', 'Surgery'),
            ('pediatrics', 'Pediatrics'),
            ('obgyn', 'OB/GYN'),
            ('dermatology', 'Dermatology'),
            ('other', 'Other'),
        ]
    )
    target_level = models.CharField(max_length=50, help_text="Student level e.g. Year 1, Intern, Resident")
    description = models.TextField()
    learning_objectives = models.TextField(blank=True)

    # الملفات
    pdf_file = models.FileField(upload_to='case_studies/pdf/', blank=True, null=True)
    image_file = models.FileField(upload_to='case_studies/images/', blank=True, null=True)

    # 🔥 NEW — Thumbnail
    thumbnail = models.ImageField(
        upload_to='case_studies/thumbnails/',
        blank=True,
        null=True,
        help_text="Thumbnail image for case study"
    )

    # 🔥 NEW — Free or Paid
    is_paid = models.BooleanField(default=False, help_text="Is this case study paid?")
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        blank=True,
        help_text="Price if case study is paid"
    )

    # بيانات الجلسة
    session_date = models.DateField()
    session_time = models.TimeField()
    zoom_meeting_id = models.CharField(max_length=50, blank=True, null=True)
    zoom_meeting_password = models.CharField(max_length=100, blank=True, null=True)


    session_status = models.CharField(
        max_length=20,
        choices=[
            ('upcoming', 'Upcoming'),
            ('ended', 'Ended'),
            ('archived', 'Archived in Library'),
        ],
        default='upcoming'
    )

    # التسجيل
    recording_file = models.FileField(upload_to='case_studies/recordings/', blank=True, null=True)
    recording_link = models.URLField(blank=True, null=True)

    # Quiz و Comments
    quiz = models.JSONField(blank=True, null=True, help_text="Optional quiz in JSON")
    comments_enabled = models.BooleanField(default=True)

    # الموافقة
    APPROVAL_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='draft'
    )
    reviewed_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_case_studies'
    )
    review_notes = models.TextField(blank=True)

    # من أنشأ الحالة
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='case_studies_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # إذا الحالة مجانية — نجبر السعر يكون 0
        if not self.is_paid:
            self.price = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.discipline})"
