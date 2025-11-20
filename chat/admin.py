from django.contrib import admin
from .models import ChatRoom, ChatMessage, MessageReaction, ChatNotification

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'room_type', 'created_by', 'is_active', 'created_at']
    list_filter = ['room_type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'created_by__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'room', 'message_type', 'is_edited', 'is_deleted', 'created_at']
    list_filter = ['message_type', 'is_edited', 'is_deleted', 'created_at']
    search_fields = ['sender__email', 'content', 'room__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'reaction_type', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    search_fields = ['user__email', 'message__content']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']

@admin.register(ChatNotification)
class ChatNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__email', 'room__name']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']









