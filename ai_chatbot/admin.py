from django.contrib import admin
from .models import ChatSession, ChatMessage

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'started_at', 'ended_at')
    list_filter = ('started_at', 'ended_at')
    search_fields = ('user__username',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'sender', 'created_at', 'short_message')
    list_filter = ('sender', 'created_at')
    search_fields = ('message', 'session__user__username')

    def short_message(self, obj):
        return obj.message[:50]
    short_message.short_description = 'Message Preview'
