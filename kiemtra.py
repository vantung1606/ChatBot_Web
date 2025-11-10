# File: kiemtra.py
# MỤC ĐÍCH: Đây là một công cụ dòng lệnh (CLI) để kiểm tra và phân tích
# luồng suy nghĩ của chatbot một cách chi tiết. Nó không ảnh hưởng đến
# hoạt động của chatbot trên website.

import os
import json
import django

# --- Cấu hình môi trường Django (Rất quan trọng) ---
# Các dòng này phải được thực thi trước khi import bất kỳ thứ gì từ Django hoặc các app của bạn.
# Nó giúp cho script Python độc lập này biết cách tìm và sử dụng các thiết lập,
# model, và các thành phần khác của project Django.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CHATBOT_WEB.settings')
django.setup()
# --- Kết thúc cấu hình ---

# Sau khi đã setup môi trường, bây giờ chúng ta mới có thể import ChatBot
from Bot.ChatBot import ChatBot

# Kích hoạt màu sắc trên terminal của Windows để output dễ nhìn hơn
# Nếu bạn dùng Linux hoặc macOS, dòng này có thể không cần thiết nhưng cũng không gây hại.
os.system('') 

# In ra tiêu đề của công cụ
print("\033[94m--- CÔNG CỤ PHÂN TÍCH LUỒNG SUY NGHĨ CỦA CHATBOT ---\033[0m")

# --- KHỞI TẠO BOT ---
# Gọi hàm getBot() để lấy một thực thể (instance) duy nhất của ChatBot.
# Nhờ mẫu thiết kế Singleton, "bộ não" AI và dữ liệu chỉ được tải vào bộ nhớ một lần.
print("Đang khởi tạo bot (tải mô hình AI và dữ liệu)...")
chatbot = ChatBot.getBot()
print("\033[92mBot đã sẵn sàng. Gõ 'quit' để thoát.\033[0m")

# --- VÒNG LẶP TƯƠNG TÁC ---
# Tạo một vòng lặp vô hạn để người dùng có thể liên tục đặt câu hỏi.
while True:
    # Yêu cầu người dùng nhập câu hỏi từ bàn phím.
    # \033[93mYou: \033[0m là mã màu để chữ "You:" có màu vàng.
    user_input = input("\n\033[93mYou: \033[0m")
    
    # Điều kiện để thoát khỏi vòng lặp.
    if user_input.lower() == 'quit':
        break

    # --- YÊU CẦU BOT PHÂN TÍCH CHI TIẾT ---
    print("\n\033[95m--- QUÁ TRÌNH SUY NGHĨ CỦA BOT ---\033[0m")
    # Đây là dòng lệnh quan trọng nhất.
    # Chúng ta gọi hàm `response` của bot và truyền vào tham số `show_details=True`.
    # Tham số này chính là "công tắc" để bật chế độ "tường thuật trực tiếp",
    # khiến bot in ra tất cả các bước xử lý bên trong nó.
    response_obj = chatbot.response(user_input, show_details=True)

    # --- IN KẾT QUẢ CUỐI CÙNG ---
    print(f"\n\033[96m{'='*15} KẾT QUẢ CUỐI CÙNG {'='*18}\033[0m")
    print("Bot sẽ gửi về cho giao diện người dùng đối tượng JSON sau:")
    
    # Sử dụng thư viện `json` để in đối tượng dictionary ra một cách đẹp mắt,
    # có thụt đầu dòng (indent=4) và hỗ trợ tiếng Việt (ensure_ascii=False).
    print(json.dumps(response_obj, indent=4, ensure_ascii=False))
    
    print("\n\033[90m----------------- HẾT LƯỢT PHÂN TÍCH -----------------\033[0m")

# In thông báo kết thúc khi người dùng gõ 'quit'.
print("\n\033[91m--- KẾT THÚC CHƯƠNG TRÌNH ---\033[0m")
