from django.db import models
from users.models import User

# ========================
# Course
# ========================
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    provider = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='provided_courses')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# ========================
# Course Unit
# ========================
class CourseUnit(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='units')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    content_type_choices = [
        ('video', 'Video'),
        ('pdf', 'PDF'),
        ('text', 'Text'),
        ('zoom', 'Live Zoom')
    ]
    content_type = models.CharField(max_length=10, choices=content_type_choices)
    content_url = models.URLField(blank=True, null=True)  # رابط الفيديو أو الملف
    order = models.PositiveIntegerField(default=1)  # ترتيب الوحدة داخل الكورس
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


# ========================
# Quiz for each Unit
# ========================
class Quiz(models.Model):
    unit = models.ForeignKey(CourseUnit, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.unit.title} - {self.title}"


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
# Course Progress (for each student)
# ========================
class CourseProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='progresses')
    completed_units = models.ManyToManyField(CourseUnit, blank=True)
    completed_quizzes = models.ManyToManyField(Quiz, blank=True)
    status_choices = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='in_progress')
    certificate_url = models.URLField(blank=True, null=True)  # رابط الشهادة بعد الانتهاء
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.status})"


# ========================
# Tracking Views
# ========================
class CourseView(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_views_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='views_courses')
    viewed_at = models.DateTimeField(auto_now_add=True)

class UnitView(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='unit_views_courses')
    unit = models.ForeignKey(CourseUnit, on_delete=models.CASCADE, related_name='views_courses')
    viewed_at = models.DateTimeField(auto_now_add=True)
