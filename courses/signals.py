# courses/signals.py
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import CourseProgress

@receiver(m2m_changed, sender=CourseProgress.completed_units.through)
def update_course_progress(sender, instance, **kwargs):
    instance.update_status()
