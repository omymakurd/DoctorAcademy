from django.db import models
from users.models import User
from lectures.models import BasicLecture, ClinicalLecture

class CaseStudy(models.Model):
    title = models.CharField(max_length=255)
    symptoms = models.TextField()
    analysis = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cases_created')
    related_basic_lectures = models.ManyToManyField(BasicLecture, related_name='cases_basic', blank=True)
    related_clinical_lectures = models.ManyToManyField(ClinicalLecture, related_name='cases_clinical', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
