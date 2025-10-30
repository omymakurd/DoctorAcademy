from django.contrib import admin
from django.utils.html import format_html
from .models import Course, CourseUnit, Quiz, Question, Choice, CourseProgress, Enrollment, CourseView, UnitView

# ========================
# Inline Classes
# ========================
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

# ========================
# Course Admin
# ========================
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'provider', 'price', 'status', 'featured', 'thumbnail_preview', 'created_at')
    search_fields = ('title', 'description', 'provider__username')
    list_filter = ('status', 'featured', 'created_at')
    inlines = [CourseUnitInline]
    actions = ['approve_courses', 'mark_as_featured', 'unmark_as_featured']

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="60" height="40" style="object-fit:cover;border-radius:5px;" />',
                obj.thumbnail.url
            )
        return "—"
    thumbnail_preview.short_description = "Thumbnail"

    def approve_courses(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} course(s) approved.")
    approve_courses.short_description = "Approve selected courses"

    def mark_as_featured(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, f"{updated} course(s) marked as featured.")
    mark_as_featured.short_description = "Mark selected courses as featured"

    def unmark_as_featured(self, request, queryset):
        updated = queryset.update(featured=False)
        self.message_user(request, f"{updated} course(s) unmarked as featured.")
    unmark_as_featured.short_description = "Unmark selected courses as featured"

# ========================
# Course Unit Admin
# ========================
@admin.register(CourseUnit)
class CourseUnitAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'content_type', 'order', 'created_at')
    search_fields = ('title', 'course__title')
    inlines = [QuizInline]
    list_filter = ('content_type', 'created_at')

# ========================
# Quiz Admin
# ========================
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit', 'created_at')
    search_fields = ('title', 'unit__title')
    inlines = [QuestionInline]

# ========================
# Question Admin
# ========================
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'created_at')
    search_fields = ('text', 'quiz__title')
    inlines = [ChoiceInline]

# ========================
# Choice Admin
# ========================
@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    search_fields = ('text', 'question__text')

# ========================
# Course Progress Admin
# ========================
@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'certificate_url', 'created_at')
    search_fields = ('student__username', 'course__title')
    filter_horizontal = ('completed_units', 'completed_quizzes')

# ========================
# Enrollment Admin
# ========================
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    search_fields = ('student__username', 'course__title')

# ========================
# CourseView Admin
# ========================
@admin.register(CourseView)
class CourseViewAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'viewed_at')
    search_fields = ('student__username', 'course__title')

# ========================
# UnitView Admin
# ========================
@admin.register(UnitView)
class UnitViewAdmin(admin.ModelAdmin):
    list_display = ('student', 'unit', 'viewed_at')
    search_fields = ('student__username', 'unit__title')
