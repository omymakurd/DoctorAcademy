from django.contrib import admin
from .models import Notification

from django.utils.html import format_html

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'status_colored', 'created_at', 'updated_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'message', 'recipient__username')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['mark_as_read']

    def status_colored(self, obj):
        color = "green" if obj.is_read else "red"
        text = "Read" if obj.is_read else "Unread"
        return format_html(f'<b style="color:{color};">{text}</b>')
    status_colored.short_description = "Status"

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} notification(s) marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"


from django.contrib import admin
from .models import Notification, AdminDevice


admin.site.register(AdminDevice)
