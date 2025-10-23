from django.contrib import admin
from .models import (
    LectureCategory, BasicSystem, Discipline, BasicLecture,
    ClinicalSystem, ClinicalLecture, InteractiveNote,
    Quiz, Question, Choice, LectureProgress
)

# ========================
# Lecture Category
# ========================
@admin.register(LectureCategory)
class LectureCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type', 'created_at', 'updated_at')
    list_filter = ('category_type',)
    search_fields = ('name',)


# ========================
# Basic Sciences
# ========================
@admin.register(BasicSystem)
class BasicSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at', 'updated_at')
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ('name', 'system', 'created_at', 'updated_at')
    list_filter = ('system',)
    search_fields = ('name',)


@admin.register(BasicLecture)
class BasicLectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'discipline', 'lecture_type', 'instructor', 'get_price', 'instructor_share', 'created_at')
    list_filter = ('lecture_type', 'discipline')
    search_fields = ('title', 'discipline__name', 'instructor__username')

    def get_price(self, obj):
        return obj.module.price if obj.module else "-"
    get_price.short_description = 'Module Price'


# ========================
# Clinical Sciences
# ========================
@admin.register(ClinicalSystem)
class ClinicalSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)


@admin.register(ClinicalLecture)
class ClinicalLectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_system', 'lecture_type', 'instructor', 'get_price', 'instructor_share', 'created_at')
    list_filter = ('lecture_type',)
    search_fields = ('title', 'instructor__username')

    def get_system(self, obj):
        return obj.module.clinical_system.name if obj.module and obj.module.clinical_system else "-"
    get_system.short_description = 'System'

    def get_price(self, obj):
        return obj.module.price if obj.module else "-"
    get_price.short_description = 'Module Price'


# ========================
# Interactive Notes
# ========================
@admin.register(InteractiveNote)
class InteractiveNoteAdmin(admin.ModelAdmin):
    list_display = ('student', 'lecture_type', 'get_lecture_title', 'created_at')
    list_filter = ('lecture_type',)
    search_fields = ('student__username',)

    def get_lecture_title(self, obj):
        if obj.lecture_type == 'basic' and obj.basic_lecture:
            return obj.basic_lecture.title
        elif obj.lecture_type == 'clinical' and obj.clinical_lecture:
            return obj.clinical_lecture.title
        return "-"
    get_lecture_title.short_description = 'Lecture'


# ========================
# Quiz
# ========================
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'lecture_type', 'get_lecture', 'created_at')
    list_filter = ('lecture_type',)
    search_fields = ('title',)

    def get_lecture(self, obj):
        if obj.lecture_type == 'basic' and obj.basic_lecture:
            return obj.basic_lecture.title
        elif obj.lecture_type == 'clinical' and obj.clinical_lecture:
            return obj.clinical_lecture.title
        return "-"
    get_lecture.short_description = 'Lecture'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'correct_answer', 'created_at')
    search_fields = ('text', 'quiz__title')


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct', 'created_at')
    list_filter = ('is_correct',)
    search_fields = ('text', 'question__text')


# ========================
# Lecture Progress
# ========================
@admin.register(LectureProgress)
class LectureProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'get_lecture', 'status', 'completed_at')
    list_filter = ('status',)
    search_fields = ('student__username',)

    def get_lecture(self, obj):
        if obj.basic_lecture:
            return obj.basic_lecture.title
        elif obj.clinical_lecture:
            return obj.clinical_lecture.title
        return "-"
    get_lecture.short_description = 'Lecture'
