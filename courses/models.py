from django.db import models
from users.models import User

# ========================
# Course
# ========================
class Course(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    provider = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='provided_courses')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    featured = models.BooleanField(default=False)  # يحدد إذا يظهر على الصفحة الرئيسية
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# ========================
# Course Unit
# ========================
class CourseUnit(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('pdf', 'PDF'),
        ('text', 'Text'),
        ('zoom', 'Live Zoom'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='units')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES)
    content_url = models.URLField(blank=True, null=True)  # رابط خارجي
    content_file = models.FileField(upload_to='course_content/', blank=True, null=True)  # رفع مباشر
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def save(self, *args, **kwargs):
        # Best practice: التأكد أن المستخدم لم يترك كلا الحقلين فارغين
        if not self.content_url and not self.content_file and self.content_type != 'text':
            raise ValueError("You must provide either a file or a URL for this unit.")
        super().save(*args, **kwargs)

# ========================
# Quiz System
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
# Course Progress
# ========================
class CourseProgress(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='progresses')
    completed_units = models.ManyToManyField(CourseUnit, blank=True)
    completed_quizzes = models.ManyToManyField(Quiz, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    certificate_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.status})"

# ========================
# Enrollment
# ========================
class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"

# ========================
# Views Tracking
# ========================
class CourseView(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_views')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='views')
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} viewed {self.course.title}"

class UnitView(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='unit_views')
    unit = models.ForeignKey(CourseUnit, on_delete=models.CASCADE, related_name='views')
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} viewed {self.unit.title}"
