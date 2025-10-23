from django.contrib import admin
from .models import CaseStudy


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'discipline',
        'get_lecture',
        'media_type_display',
        'created_by',
        'created_at',
    )
    list_filter = ('discipline', 'created_at', 'updated_at')
    search_fields = (
        'title',
        'symptoms',
        'analysis',
        'created_by__username',
    )
    readonly_fields = ('created_at', 'updated_at', 'media_preview')
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
        """عرض اسم المحاضرة المرتبطة"""
        if obj.basic_lecture:
            return f"Basic: {obj.basic_lecture.title}"
        elif obj.clinical_lecture:
            return f"Clinical: {obj.clinical_lecture.title}"
        return "-"
    get_lecture.short_description = "Lecture"

    def media_type_display(self, obj):
        """عرض نوع الوسائط بلغة واضحة"""
        types = {
            "file_video": "Uploaded Video",
            "external_video": "Video URL",
            "file_attachment": "Attachment",
            "text_only": "Text Only",
        }
        return types.get(obj.get_media_type(), "Unknown")
    media_type_display.short_description = "Media Type"

    def media_preview(self, obj):
        """عرض معاينة بسيطة للوسائط"""
        if obj.video_url:
            return f'<a href="{obj.video_url}" target="_blank">Watch External Video</a>'
        elif obj.video:
            return f'<a href="{obj.video.url}" target="_blank">Download/Watch Uploaded Video</a>'
        elif obj.attachment:
            return f'<a href="{obj.attachment.url}" target="_blank">View Attachment</a>'
        return "No media attached"
    media_preview.allow_tags = True
    media_preview.short_description = "Media Preview"
