from django.contrib import admin
from .models import Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('timestamp',)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'agent_type', 'created_at')
    list_filter = ('agent_type', 'created_at')
    search_fields = ('id', 'agent_type')
    inlines = [MessageInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('get_conversation_id', 'is_user', 'content_preview', 'timestamp')
    list_filter = ('is_user', 'timestamp')
    search_fields = ('content',)
    
    def get_conversation_id(self, obj):
        return obj.conversation.id
    get_conversation_id.short_description = 'Conversation ID'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content' 