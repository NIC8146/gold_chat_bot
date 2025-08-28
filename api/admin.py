from django.contrib import admin
from .models import UserProfile, ChatSession, ChatMessage, GoldTransaction

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'created_at')

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'title', 'created_at')
    list_filter = ('user',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'session', 'role', 'content_preview', 'timestamp')
    list_filter = ('session', 'role')
    
    def content_preview(self, obj):
        return (obj.content[:50] + '...') if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(GoldTransaction)
class GoldTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id', 'user_name', 'weight_in_grams',
        'gold_rate_per_gram_usd', 'total_price_usd', 'timestamp'
    )
    list_filter = ('user_name',)
