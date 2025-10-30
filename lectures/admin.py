from django.contrib import admin
from .models import (
    LectureCategory, BasicSystem, Discipline, ClinicalSystem, Module,
    BasicLecture, ClinicalLecture, InteractiveNote, Quiz, Question, Choice,
    LectureProgress, ModuleEnrollment, ModuleProgress, VideoAccessToken,
    LectureReview, Certificate, InstructorEarning, PaymentMethod, PaymentTransaction
)

@admin.register(LectureCategory)
class LectureCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type', 'created_at')
    search_fields = ('name',)

@admin.register(BasicSystem)
class BasicSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name',)

@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ('system', 'get_name_display')
    search_fields = ('system__name',)

@admin.register(ClinicalSystem)
class ClinicalSystemAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'price', 'status', 'is_featured', 'created_at')
    list_filter = ('status', 'is_featured')
    search_fields = ('title', 'instructor__username')

@admin.register(BasicLecture)
class BasicLectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'discipline', 'lecture_type', 'order')
    list_filter = ('lecture_type',)
    search_fields = ('title',)

@admin.register(ClinicalLecture)
class ClinicalLectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'lecture_type', 'order')
    list_filter = ('lecture_type',)
    search_fields = ('title',)

admin.site.register([InteractiveNote, Quiz, Question, Choice, LectureProgress,
                     ModuleEnrollment, ModuleProgress, VideoAccessToken,
                     LectureReview, Certificate, InstructorEarning,
                     PaymentMethod, PaymentTransaction])
