from django.db import models
from users.models import User
from courses.models import Course, CourseUnit

class CourseView(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_views_analytics')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='views_analytics')
    viewed_at = models.DateTimeField(auto_now_add=True)

class UnitView(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='unit_views_analytics')
    unit = models.ForeignKey(CourseUnit, on_delete=models.CASCADE, related_name='views_analytics')
    viewed_at = models.DateTimeField(auto_now_add=True)
