from django.db import models
from users.models import User

# ========================
# Lecture Categories
# ========================
class LectureCategory(models.Model):
    CATEGORY_TYPES = [
        ('basic', 'Basic Sciences'),
        ('clinical', 'Clinical Medicine'),
    ]
    name = models.CharField(max_length=255)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category_type})"


# ========================
# Basic Sciences
# ========================
class BasicSystem(models.Model):
    category = models.ForeignKey(LectureCategory, on_delete=models.CASCADE, related_name='basic_systems')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.category.name}"


class Discipline(models.Model):
    system = models.ForeignKey(BasicSystem, on_delete=models.CASCADE, related_name='disciplines')
    DISCIPLINE_CHOICES = [
        ('anatomy','Anatomy'),
        ('embryology','Embryology'),
        ('histology','Histology'),
        ('physiology','Physiology'),
        ('pathology','Pathology'),
        ('pharmacology','Pharmacology'),
    ]
    name = models.CharField(max_length=20, choices=DISCIPLINE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.system.name} - {self.get_name_display()}"


class BasicLecture(models.Model):
    discipline = models.ForeignKey('Discipline', on_delete=models.CASCADE, related_name='lectures')
    title = models.CharField(max_length=255)
    lecture_type = models.CharField(max_length=20, choices=[('recorded','Recorded Video'),('zoom','Live Zoom')])
    video_url = models.URLField(blank=True, null=True)
    zoom_link = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='basic_lectures')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    instructor_share = models.DecimalField(max_digits=5, decimal_places=2, default=50.0)  # نسبة أرباح المحاضر
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# ========================
# Clinical Sciences
# ========================
class ClinicalSystem(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ClinicalLecture(models.Model):
    system = models.ForeignKey('ClinicalSystem', on_delete=models.CASCADE, related_name='lectures')
    title = models.CharField(max_length=255)
    lecture_type = models.CharField(max_length=20, choices=[('recorded','Recorded Video'),('zoom','Live Zoom')])
    video_url = models.URLField(blank=True, null=True)
    zoom_link = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='clinical_lectures')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    instructor_share = models.DecimalField(max_digits=5, decimal_places=2, default=50.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.system.name} - {self.title}"


# ========================
# Interactive Notes
# ========================
class InteractiveNote(models.Model):
    lecture_type_choices = [
        ('basic', 'BasicLecture'),
        ('clinical', 'ClinicalLecture'),
    ]
    lecture_type = models.CharField(max_length=10, choices=lecture_type_choices)
    basic_lecture = models.ForeignKey(BasicLecture, on_delete=models.CASCADE, null=True, blank=True)
    clinical_lecture = models.ForeignKey(ClinicalLecture, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.lecture_type == 'basic':
            return f"Note by {self.student.username} on {self.basic_lecture.title}"
        else:
            return f"Note by {self.student.username} on {self.clinical_lecture.title}"


# ========================
# Case Studies
# ========================


# ========================
# Quiz / Question / Choice
# ========================
class Quiz(models.Model):
    lecture_type_choices = [
        ('basic', 'BasicLecture'),
        ('clinical', 'ClinicalLecture'),
    ]
    lecture_type = models.CharField(max_length=10, choices=lecture_type_choices)
    basic_lecture = models.ForeignKey(BasicLecture, on_delete=models.CASCADE, null=True, blank=True)
    clinical_lecture = models.ForeignKey(ClinicalLecture, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    correct_answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text[:50]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text


# ========================
# Lecture Progress
# ========================
class LectureProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lecture_progress')
    basic_lecture = models.ForeignKey(BasicLecture, on_delete=models.CASCADE, null=True, blank=True)
    clinical_lecture = models.ForeignKey(ClinicalLecture, on_delete=models.CASCADE, null=True, blank=True)
    status_choices = [('in_progress','In Progress'),('completed','Completed')]
    status = models.CharField(max_length=20, choices=status_choices, default='in_progress')
    completed_at = models.DateTimeField(null=True, blank=True)
