from django.contrib import admin
from .models import CourseView, UnitView

@admin.register(CourseView)
class CourseViewAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'course', 'viewed_at')
    list_filter = ('course', 'viewed_at')
    search_fields = ('student__username', 'course__title')

@admin.register(UnitView)
class UnitViewAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'unit', 'viewed_at')
    list_filter = ('unit', 'viewed_at')
    search_fields = ('student__username', 'unit__title')
