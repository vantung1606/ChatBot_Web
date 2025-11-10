from django.db import models

class Intent(models.Model):
    tag = models.CharField(max_length=255, unique=True, help_text="Tên định danh duy nhất của ý định, ví dụ: 'greeting', 'prod_ao_mu'")
    product_page_url = models.URLField(max_length=2048, blank=True, null=True, help_text="(Tùy chọn) Link đến trang sản phẩm nếu đây là intent về sản phẩm.")

    def __str__(self):
        return self.tag

class Pattern(models.Model):
    intent = models.ForeignKey(Intent, related_name='patterns', on_delete=models.CASCADE)
    text = models.CharField(max_length=512, help_text="Một mẫu câu hỏi của người dùng, ví dụ: 'Xin chào', 'áo mu giá bao nhiêu?'")

    def __str__(self):
        return self.text

class Response(models.Model):
    intent = models.ForeignKey(Intent, related_name='responses', on_delete=models.CASCADE)
    text = models.CharField(max_length=1024, help_text="Một câu trả lời của bot, ví dụ: 'Chào bạn! Shop có thể giúp gì cho bạn?'")

    def __str__(self):
        return self.text
