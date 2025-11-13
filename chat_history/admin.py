from django.contrib import admin
from .models import ChatHistory

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    """
    Tùy chỉnh cách hiển thị model ChatHistory trong trang admin.
    """
    list_display = ('customer_id', 'user_message_snippet', 'bot_response_snippet', 'timestamp')
    list_filter = ('timestamp', 'customer_id')
    search_fields = ('user_message', 'bot_response')
    readonly_fields = ('timestamp',) # Không cho phép sửa đổi thời gian

    def user_message_snippet(self, obj):
        return obj.user_message[:50] + '...' if len(obj.user_message) > 50 else obj.user_message
    user_message_snippet.short_description = 'User Message'

    def bot_response_snippet(self, obj):
        # Chuyển đổi dict thành chuỗi để hiển thị
        response_str = str(obj.bot_response)
        return response_str[:70] + '...' if len(response_str) > 70 else response_str
    bot_response_snippet.short_description = 'Bot Response'
