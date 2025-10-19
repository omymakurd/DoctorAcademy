from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, InstructorProfile, CourseProviderProfile, StudentProfile

# ========================
# User
# ========================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_verified', 'status', 'is_staff', 'is_superuser', 'created_at')
    list_filter = ('role', 'is_verified', 'status', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'phone', 'role', 'is_verified', 'status')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

# ========================
# Instructor Profile
# ========================
@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'default_profit_share', 'created_at')
    search_fields = ('user__username', 'specialization')
    readonly_fields = ('created_at', 'updated_at')

# ========================
# Course Provider Profile
# ========================
@admin.register(CourseProviderProfile)
class CourseProviderProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'entity_name', 'profit_share', 'created_at')
    search_fields = ('user__username', 'entity_name')
    readonly_fields = ('created_at', 'updated_at')

# ========================
# Student Profile
# ========================
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'university', 'year', 'created_at')
    search_fields = ('user__username', 'university')
    readonly_fields = ('created_at', 'updated_at')
