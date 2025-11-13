from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from Bot.ChatBot import ChatBot

# --- THAY ĐỔI QUAN TRỌNG ---
# Khởi tạo chatbot_instance là None ở cấp độ module.
# Chúng ta sẽ không khởi tạo bot ngay lập tức để tránh lỗi "con gà và quả trứng"
# khi chạy các lệnh `makemigrations` và `migrate`.
chatbot_instance = None

def index(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render({}, request))

@csrf_exempt # Tạm thời bỏ qua kiểm tra CSRF để test API dễ hơn
def chat_api(request):
    # ✅ THAY ĐỔI: Đảm bảo chatbot chỉ được khởi tạo một lần duy nhất
    # bằng cách sử dụng biến global và kiểm tra xem nó đã được khởi tạo chưa.
    global chatbot_instance
    if chatbot_instance is None:
        print("Initializing ChatBot for the first time...")
        chatbot_instance = ChatBot.getBot()
        print("ChatBot Initialized and ready.")

    if request.method == 'POST':
        try:
            # Lấy dữ liệu JSON mà frontend gửi lên
            data = json.loads(request.body)
            # Lấy tin nhắn từ dữ liệu
            user_message = data.get('message')

            # Lấy customer_id từ frontend gửi lên.
            # Frontend sẽ gửi `null` hoặc không gửi trường này nếu người dùng chưa đăng nhập (chưa login).
            customer_id = data.get('customer_id')
 
            # --- ✅ BƯỚC QUAN TRỌNG: KIỂM TRA XEM NGƯỜI DÙNG ĐÃ ĐĂNG NHẬP CHƯA ---
            # Nếu không có customer_id (là null, 0, hoặc không tồn tại), yêu cầu đăng nhập.
            if not customer_id:
                return JsonResponse({
                    'response': {
                        'type': 'auth_required',
                        'text': 'Bạn cần đăng nhập để có thể bắt đầu trò chuyện. Nhấn vào đây để đăng nhập nhé!',
                        # Thêm link đăng nhập để frontend có thể điều hướng
                        'link': 'http://localhost:8080/dang-nhap' 
                    }
                })

            if user_message:
                # Dùng bot đã được khởi tạo để lấy câu trả lời
                response_message = chatbot_instance.response(user_message)

              

                # Trả về câu trả lời dưới dạng JSON
                return JsonResponse({'response': response_message})
            else:
                return JsonResponse({'error': 'No message provided'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
 
    return JsonResponse({'error': 'Invalid request method'}, status=405)