from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import CaseStudy


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'discipline', 'get_lecture', 'media_type_display', 'created_by', 'created_at')
    list_filter = ('discipline', 'created_at', 'updated_at')
    search_fields = ('title', 'symptoms', 'analysis', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at', 'media_preview')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'discipline', 'symptoms', 'analysis', 'created_by')
        }),
        ('Lecture Relation', {
            'fields': ('basic_lecture', 'clinical_lecture')
        }),
        ('Media', {
            'fields': ('video', 'video_url', 'attachment', 'media_preview')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_lecture(self, obj):
        if obj.basic_lecture:
            return f"Basic: {obj.basic_lecture.title}"
        elif obj.clinical_lecture:
            return f"Clinical: {obj.clinical_lecture.title}"
        return "-"
    get_lecture.short_description = "Lecture"

    def media_type_display(self, obj):
        types = {
            "file_video": "Uploaded Video",
            "external_video": "Video URL",
            "file_attachment": "Attachment",
            "text_only": "Text Only",
        }
        return types.get(obj.get_media_type(), "Unknown")
    media_type_display.short_description = "Media Type"

    def media_preview(self, obj):
        if obj.video_url:
            return mark_safe(f'<a href="{obj.video_url}" target="_blank">Watch External Video</a>')
        elif obj.video:
            return mark_safe(f'<a href="{obj.video.url}" target="_blank">Download/Watch Uploaded Video</a>')
        elif obj.attachment:
            return mark_safe(f'<a href="{obj.attachment.url}" target="_blank">View Attachment</a>')
        return "No media attached"
    media_preview.short_description = "Media Preview"
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.html import format_html
from .models import CaseStudyNew


@admin.register(CaseStudyNew)
class CaseStudyNewAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'discipline', 'target_level', 'session_date',
        'session_time', 'session_status', 'approval_status_display',
        'approve_reject_actions', 'created_by', 'created_at'
    )
    list_filter = ('discipline', 'session_status', 'approval_status', 'created_at')
    search_fields = ('title', 'description', 'learning_objectives', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at', 'recording_preview', 'zoom_link_display')
    ordering = ('-created_at',)
    date_hierarchy = 'session_date'

    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'discipline', 'target_level', 'description', 'learning_objectives', 'created_by')
        }),
        ('Attachments', {
            'fields': ('pdf_file', 'image_file', 'thumbnail')
        }),
        ('Session Info', {
            'fields': ('session_date', 'session_time', 'zoom_meeting_id', 'zoom_link_display',
                       'session_status', 'recording_file', 'recording_link', 'recording_preview')
        }),
        ('Pricing', {
            'fields': ('is_paid', 'price')
        }),
        ('Approval', {
            'fields': ('approval_status', 'reviewed_by', 'review_notes', 'comments_enabled')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
        ('Quiz', {
            'fields': ('quiz',)
        }),
    )

    # عرض رابط التسجيل أو تحميله
    def recording_preview(self, obj):
        if obj.recording_link:
            return mark_safe(f'<a href="{obj.recording_link}" target="_blank">Watch Recording Link</a>')
        elif obj.recording_file:
            return mark_safe(f'<a href="{obj.recording_file.url}" target="_blank">Download/Watch Uploaded Recording</a>')
        return "No recording available"
    recording_preview.short_description = "Recording Preview"

    # عرض رابط الزوم
    def zoom_link_display(self, obj):
        if obj.zoom_meeting_id:
            return mark_safe(f'<a href="https://zoom.us/j/{obj.zoom_meeting_id}" target="_blank">Join Zoom Meeting</a>')
        return "-"
    zoom_link_display.short_description = "Zoom Link"

    # عرض حالة الموافقة مع ألوان
    def approval_status_display(self, obj):
        colors = {
            'draft': 'gray',
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red'
        }
        color = colors.get(obj.approval_status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.approval_status.capitalize()
        )
    approval_status_display.short_description = "Approval Status"

    # أزرار الموافقة/الرفض
    def approve_reject_actions(self, obj):
        buttons = []
        if obj.approval_status != 'approved':
            approve_url = reverse('admin:cases_casestudynew_change', args=[obj.id])
            buttons.append(format_html(
                '<a class="button" href="{}?approval_status=approved">✅ Approve</a>',
                approve_url
            ))
        if obj.approval_status != 'rejected':
            reject_url = reverse('admin:cases_casestudynew_change', args=[obj.id])
            buttons.append(format_html(
                '<a class="button" style="color:red;" href="{}?approval_status=rejected">❌ Reject</a>',
                reject_url
            ))
        return format_html(" &nbsp; ".join(buttons)) if buttons else "-"
    approve_reject_actions.short_description = "Actions"
