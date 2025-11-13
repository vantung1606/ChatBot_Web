import os
import django

# --- Cấu hình môi trường Django (Rất quan trọng) ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CHATBOT_WEB.settings')
django.setup()
# --- Kết thúc cấu hình ---

import nltk
import numpy as np
import tflearn
import random
import pickle
import json
from Bot import path
from intent_manager.models import Intent # ✅ Lấy dữ liệu từ model
nltk.download('punkt')


class ChatBot(object):

    instance = None
    # Đảm bảo bộ nhớ chỉ lưu 1 lần
    @classmethod
    def getBot(cls):
        if cls.instance is None:
            cls.instance = ChatBot()
        return cls.instance

    def __init__(self):
        print("Init")
        if self.instance is not None:
            raise ValueError("Did you forgot to call getBot function ? ")

        data = pickle.load(open(path.getPath('trained_data'), "rb"))
        self.words = data['words']
        self.classes = data['classes']
        train_x = data['train_x']
        train_y = data['train_y']
        self.context = {} 
        
        # ✅ THAY ĐỔI LỚN: Lấy toàn bộ intent từ DB và lưu vào một dictionary để truy cập nhanh
        print("Loading intents from database into memory...")
        self.intents_from_db = {
            intent.tag: intent for intent in Intent.objects.prefetch_related('responses').all()
        }
        print(f"Loaded {len(self.intents_from_db)} intents.")

        # Tái tạo lại kiến trúc mạng nơ-ron
        net = tflearn.input_data(shape=[None, len(train_x[0])])
        net = tflearn.fully_connected(net, 16) # ✅ THAY ĐỔI: Phải giống với file train.py
        net = tflearn.fully_connected(net, 16) # ✅ THAY ĐỔI: Phải giống với file train.py
        net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
        net = tflearn.regression(net)
        # Tải trọng số (kiến thức) đã huấn luyện vào mô hình
        self.model = tflearn.DNN(net, tensorboard_dir=path.getPath('train_logs'))
        self.model.load(path.getPath('model.tflearn'))

    def clean_up_sentence(self, sentence):
        # Hàm này không cần show_details vì nó được gọi từ bow() và response() đã có giải thích
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [word.lower() for word in sentence_words] # ✅ THAY ĐỔI: Chỉ chuyển về chữ thường
        return sentence_words

    def bow(self, sentence, words, show_details=False):
        sentence_words = self.clean_up_sentence(sentence)
        if show_details:
            print(f"   - Các từ đã xử lý trong câu: {sentence_words}")
            print(f"   - So khớp với từ điển của Bot ({len(words)} từ)...")

        bag = [0] * len(words)
        for s in sentence_words:
            for i, w in enumerate(words):
                if w == s:
                    bag[i] = 1
                    if show_details:
                        print(f"     -> Tìm thấy từ '{w}' trong từ điển. Đánh dấu '1' vào vector.")
        return np.array(bag)
        
    # Dự đoán ý định
    def classify(self, sentence, error_threshold, show_details=False):
        # Tạo vector Bag of Words
        bow_vector = self.bow(sentence, self.words, show_details=show_details)
        if show_details:
            print(f"   - Vector 'Túi từ' cuối cùng đã được tạo. Bắt đầu đưa vào mô hình AI để dự đoán.")

        results = self.model.predict([bow_vector])[0]
        
        # Lọc ra các kết quả có xác suất thấp
        results = [[i, r] for i, r in enumerate(results) if r > error_threshold]
        # Sắp xếp theo thứ tự xác suất giảm dần
        results.sort(key=lambda x: x[1], reverse=True)
        
        return_list = []
        for r in results:
            return_list.append((self.classes[r[0]], r[1]))
        return return_list
        
    # ✅ HÀM RESPONSE ĐÃ CHUẨN HÓA - LUÔN TRẢ VỀ DICTIONARY
    def response(self, sentence, userID='111', show_details=False):
        # ✅ ĐỊNH NGHĨA CÁC NGƯỠNG Ở ĐÂY
        ERROR_THRESHOLD = 0.1  # Ngưỡng tối thiểu để một dự đoán được xem xét

        CONFIDENCE_THRESHOLD = 0.3 # Ngưỡng tối thiểu để bot tự tin trả lời

        if show_details: # Bắt đầu tường thuật
            print(f"\n{'='*15} BƯỚC 1: TIỀN XỬ LÝ & MÃ HÓA {'='*14}")
            print(f"Mục tiêu: Biến câu '{sentence}' thành một vector số mà AI có thể hiểu.")

        # Gọi hàm classify, hàm này sẽ tự động gọi bow và clean_up_sentence
        # và in ra các bước chi tiết nếu show_details=True
        results = self.classify(sentence, error_threshold=ERROR_THRESHOLD, show_details=show_details)

        # CẢI TIẾN: Chỉ xử lý nếu có kết quả và độ tin cậy đủ cao
        if results:
            intent_tag, probability = results[0] # Lấy tag và độ tin cậy cao nhất
            if show_details:
                print(f"\n{'='*15} BƯỚC 2: DỰ ĐOÁN Ý ĐỊNH {'='*17}")
                print(f"Mô hình AI đã phân tích và đưa ra các dự đoán sau (với độ tin cậy > {ERROR_THRESHOLD:.0%}):")
                for r in results:
                    print(f"   - Ý định: '{r[0]}', Độ tin cậy: {r[1]:.2%}")

                print(f"\n{'='*15} BƯỚC 3: RA QUYẾT ĐỊNH {'='*18}")
                print(f"So sánh độ tin cậy của ý định cao nhất ('{intent_tag}' - {probability:.2%}) với ngưỡng quyết định ({CONFIDENCE_THRESHOLD:.2%}).")

            if probability > CONFIDENCE_THRESHOLD:

                if show_details:
                    print(f"   -> KẾT LUẬN: Đủ tin cậy. Bot sẽ tìm câu trả lời trong database cho tag '{intent_tag}'.")


                if show_details: 
                    print(f"   -> KẾT LUẬN: Đủ tin cậy. Bot sẽ tìm câu trả lời trong database cho tag '{intent_tag}'.")
                

                # ✅ THAY ĐỔI LỚN: Tìm intent trong dictionary đã tải từ DB
                intent_obj = self.intents_from_db.get(intent_tag)
                if intent_obj:
                    # Lấy danh sách các câu trả lời từ đối tượng intent
                    responses_list = [resp.text for resp in intent_obj.responses.all()]
                    if not responses_list:
                        return {"type": "text", "text": f"(Lỗi hệ thống: Intent '{intent_tag}' không có câu trả lời nào trong DB)"}

                    # 1. Nếu là intent sản phẩm
                    if intent_obj.product_page_url:
                        return {"type": "product", "text": random.choice(responses_list), "link": intent_obj.product_page_url}
                    # 2. Nếu là intent thông thường
                    else:
                        self.context.pop(userID, None)
                        return {"type": "text", "text": random.choice(responses_list)}

            else:


                if show_details: 
                    print(f"   -> KẾT LUẬN: Không đủ tin cậy. Kích hoạt chế độ trả lời mặc định (Fallback).")
                return { "type": "text", "text": self.smart_fallback_response(sentence, userID, show_details=show_details) }

        # 3. Nếu không phân loại được hoặc độ tin cậy quá thấp (fallback)
        if show_details:
            print(f"\n{'='*15} BƯỚC 2: DỰ ĐOÁN Ý ĐỊNH {'='*17}")
            print(f"Mô hình AI không tìm thấy ý định nào có độ tin cậy lớn hơn ngưỡng lỗi ({ERROR_THRESHOLD:.0%}).")
            print(f"\n{'='*15} BƯỚC 3: RA QUYẾT ĐỊNH {'='*18}")
            print("   -> KẾT LUẬN: Không thể xác định ý định. Kích hoạt chế độ trả lời mặc định (Fallback).")
        return {
            "type": "text",
            "text": self.smart_fallback_response(sentence, userID, show_details=show_details)
        }

    # === HÀM FALLBACK (ĐÃ ĐÚNG) ===
    def smart_fallback_response(self, sentence, userID='111', show_details=False):
        """
        Xử lý các câu hỏi ngoài phạm vi training một cách thông minh.
        """
        if show_details:
            print("\n   --- Phân tích bên trong chế độ Fallback ---")
            print("   Mục tiêu: Tìm một câu trả lời phù hợp dựa trên các từ khóa định sẵn, thay vì dùng AI.")

        sentence_lower = sentence.lower()
        
        # Kiểm tra các từ khóa liên quan đến bóng đá (chung chung)
        football_keywords = ['bóng đá', 'football', 'soccer', 'clb', 'đội tuyển', 'cầu thủ', 'sân', 'trận đấu']
        if any(keyword in sentence_lower for keyword in football_keywords):
            if show_details:
                found_keyword = next((k for k in football_keywords if k in sentence_lower), None)
                print(f"   -> KIỂM TRA 1: Tìm thấy từ khóa '{found_keyword}' thuộc nhóm 'bóng đá'. Chọn câu trả lời tương ứng.")
            return "Mình hiểu bạn đang hỏi về bóng đá! Shop chuyên về áo bóng đá và phụ kiện. Bạn muốn tìm áo/giày/phụ kiện nào cụ thể không?"
        
        # Kiểm tra các từ khóa về mua sắm (chung chung)
        shopping_keywords = ['mua', 'bán', 'giá', 'tiền', 'đặt hàng', 'thanh toán']
        if any(keyword in sentence_lower for keyword in shopping_keywords):
            if show_details:
                found_keyword = next((k for k in shopping_keywords if k in sentence_lower), None)
                print(f"   -> KIỂM TRA 2: Tìm thấy từ khóa '{found_keyword}' thuộc nhóm 'mua sắm'. Chọn câu trả lời tương ứng.")
            return "Bạn muốn mua hàng phải không? Bạn có thể hỏi mình về sản phẩm cụ thể (ví dụ: 'Áo CLB Barcelona 2024-2025 giá bao nhiêu?') và mình sẽ báo giá nhé!"
        
        # Kiểm tra các từ khóa về thể thao khác (để từ chối)
        other_sports = ['bóng rổ', 'tennis', 'cầu lông', 'bơi lội', 'gym', 'fitness', 'bóng chuyền', 'bóng bàn', 'bơi', 'chạy']
        if any(sport in sentence_lower for sport in other_sports):
            if show_details:
                found_keyword = next((k for k in other_sports if k in sentence_lower), None)
                print(f"   -> KIỂM TRA 3: Tìm thấy từ khóa '{found_keyword}' thuộc nhóm 'thể thao khác'. Chọn câu trả lời từ chối.")
            return "Xin lỗi, shop chỉ chuyên về áo bóng đá thôi ạ! Mình có thể giúp bạn tìm áo CLB hoặc áo tuyển quốc gia nhé!"
        
        # Kiểm tra các câu hỏi cá nhân (để từ chối)
        personal_keywords = ['tên', 'tuổi', 'ở đâu', 'làm gì', 'nghề nghiệp']
        if any(keyword in sentence_lower for keyword in personal_keywords):
            if show_details:
                found_keyword = next((k for k in personal_keywords if k in sentence_lower), None)
                print(f"   -> KIỂM TRA 4: Tìm thấy từ khóa '{found_keyword}' thuộc nhóm 'cá nhân'. Chọn câu trả lời tương ứng.")
            return "Mình là chatbot của shop áo bóng đá! Mình có thể giúp bạn tìm sản phẩm, tư vấn size, giá cả... Bạn cần hỗ trợ gì?"
        
        # Gộp chung các chủ đề không liên quan
        off_topic_keywords = [
            'thời tiết', 'tin tức', 'chính trị', 'kinh tế', 'covid',
            'máy tính', 'điện thoại', 'app', 'website', 'lập trình', 'code',
            'ăn', 'uống', 'nhà hàng', 'cafe', 'món ăn',
            'du lịch', 'đi chơi', 'khách sạn', 'vé máy bay',
            'học', 'trường', 'sinh viên', 'bài tập', 'thi cử',
            'bệnh', 'thuốc', 'bác sĩ', 'sức khỏe', 'y tế',
            'yêu', 'thích', 'bạn gái', 'bạn trai',
            'công việc', 'làm việc', 'lương',
            'phim', 'nhạc', 'game', 'ca sĩ',
            'tài chính', 'ngân hàng', 'đầu tư',
            'xe', 'ô tô', 'xe máy',
            'nhà', 'căn hộ', 'thuê nhà',
            'chó', 'mèo', 'thú cưng',
            'vẽ', 'hội họa', 'âm nhạc', 'nghệ thuật',
            'mấy giờ', 'thời gian', 'ngày', 'tháng',
            'địa lý', 'lịch sử', 'khoa học', 'tôn giáo'
        ]
        
        if any(keyword in sentence_lower for keyword in off_topic_keywords):
            if show_details:
                found_keyword = next((k for k in off_topic_keywords if k in sentence_lower), None)
                print(f"   -> KIỂM TRA 5: Tìm thấy từ khóa '{found_keyword}' thuộc nhóm 'không liên quan'. Chọn câu trả lời từ chối.")
            return "Mình chỉ biết về áo bóng đá và các phụ kiện thể thao thôi ạ! Bạn có thể hỏi mình về các sản phẩm của shop nhé!"

        
        # Câu trả lời mặc định cuối cùng
        if show_details: print("   -> KIỂM TRA CUỐI: Không tìm thấy từ khóa nào phù hợp trong tất cả các nhóm. Trả về câu trả lời mặc định cuối cùng.")
        return ("Xin lỗi, mình chưa hiểu câu hỏi của bạn. Mình chỉ biết về các sản phẩm áo bóng đá và phụ kiện của shop thôi!\n"
                "Bạn có thể hỏi mình về:\n"
                "- Tên sản phẩm cụ thể (ví dụ: 'Áo CLB Barcelona 2024-2025')\n"
                "- Các chủ đề chung như 'size', 'giao hàng', 'khuyến mãi'...")