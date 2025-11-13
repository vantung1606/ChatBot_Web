from django.db import models

class ChatHistory(models.Model):
    """
    Model để lưu lại lịch sử chat của người dùng.
    """
    # Thay vì dùng ForeignKey, ta dùng IntegerField để lưu ID của khách hàng
    # từ bảng `customer` của CodeIgniter.
    customer_id = models.IntegerField(help_text="ID của khách hàng từ bảng customer")
    
    user_message = models.TextField(help_text="Tin nhắn của người dùng")
    
    # Lưu toàn bộ đối tượng JSON mà bot trả về
    bot_response = models.JSONField(help_text="Đối tượng JSON phản hồi từ bot")
    
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Thời gian chat")

    def __str__(self):
        return f"Chat của customer ID {self.customer_id} lúc {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
