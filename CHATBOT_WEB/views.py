from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def index(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render({}, request))
from Bot.ChatBot import ChatBot

# --- Rất quan trọng: Khởi tạo bot một lần duy nhất ---
# Việc này giúp không phải tải lại mô hình AI mỗi khi có tin nhắn mới, tiết kiệm rất nhiều thời gian.
print("Initializing ChatBot...")
chatbot_instance = ChatBot.getBot()
print("ChatBot Initialized.")

@csrf_exempt # Tạm thời bỏ qua kiểm tra CSRF để test API dễ hơn
def chat_api(request):
    # Chỉ chấp nhận các request gửi bằng phương thức POST
    if request.method == 'POST':
        try:
            # Lấy dữ liệu JSON mà frontend gửi lên
            data = json.loads(request.body)
            # Lấy tin nhắn từ dữ liệu
            message = data.get('message')

            if message:
                # Dùng bot đã được khởi tạo để lấy câu trả lời
                response_message = chatbot_instance.response(message)
                # Trả về câu trả lời dưới dạng JSON
                return JsonResponse({'response': response_message})
            else:
                return JsonResponse({'error': 'No message provided'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)