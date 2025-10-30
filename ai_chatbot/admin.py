from django.contrib import admin
from .models import ChatSession, ChatMessage


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'started_at', 'ended_at', 'active_status')
    list_filter = ('started_at', 'ended_at')
    search_fields = ('user__username',)
    date_hierarchy = 'started_at'
    ordering = ('-started_at',)

    def active_status(self, obj):
        return "Active" if not obj.ended_at else "Ended"
    active_status.short_description = 'Status'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'sender', 'created_at', 'short_message')
    list_filter = ('sender', 'created_at')
    search_fields = ('message', 'session__user__username')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    def short_message(self, obj):
        return (obj.message[:47] + "...") if len(obj.message) > 50 else obj.message
    short_message.short_description = 'Message Preview'
