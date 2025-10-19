from django.contrib import admin
from .models import Course, CourseUnit, Quiz, Question, Choice, CourseProgress, CourseView, UnitView

class CourseUnitInline(admin.TabularInline):
    model = CourseUnit
    extra = 1

class QuizInline(admin.TabularInline):
    model = Quiz
    extra = 1

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'provider', 'price', 'created_at')
    search_fields = ('title', 'description', 'provider__username')
    inlines = [CourseUnitInline]

@admin.register(CourseUnit)
class CourseUnitAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'content_type', 'order', 'created_at')
    search_fields = ('title', 'course__title')
    inlines = [QuizInline]

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit', 'created_at')
    search_fields = ('title', 'unit__title')
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'created_at')
    search_fields = ('text', 'quiz__title')
    inlines = [ChoiceInline]

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    search_fields = ('text', 'question__text')

@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'certificate_url', 'created_at')
    search_fields = ('student__username', 'course__title')

@admin.register(CourseView)
class CourseViewAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'viewed_at')
    search_fields = ('student__username', 'course__title')

@admin.register(UnitView)
class UnitViewAdmin(admin.ModelAdmin):
    list_display = ('student', 'unit', 'viewed_at')
    search_fields = ('student__username', 'unit__title')
