from django.contrib import admin
from .models import CaseStudy

@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_by', 'created_at', 'updated_at')
    search_fields = ('title', 'symptoms', 'analysis', 'created_by__username')
    list_filter = ('created_at', 'updated_at')
    filter_horizontal = ('related_basic_lectures', 'related_clinical_lectures')
