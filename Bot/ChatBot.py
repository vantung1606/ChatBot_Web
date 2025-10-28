import nltk
from nltk.stem.lancaster import LancasterStemmer

import numpy as np
import tflearn
import random

import pickle
import json
from Bot import path
nltk.download('punkt')


class ChatBot(object):

    instance = None
    # đảm bảo bộ nhớ chỉ lưu 1 lần
    @classmethod
    def getBot(cls):
        if cls.instance is None:
            cls.instance = ChatBot()
        return cls.instance

    def __init__(self):
        print("Init")
        if self.instance is not None:
            raise ValueError("Did you forgot to call getBot function ? ")

        self.stemmer = LancasterStemmer()
        data = pickle.load(open(path.getPath('trained_data'), "rb"))
        self.words = data['words']
        self.classes = data['classes']
        train_x = data['train_x']
        train_y = data['train_y']
        self.context = {} 
        # Sửa lại thành như sau
        with open(path.getJsonPath(), encoding='utf-8') as json_data:
            self.intents = json.load(json_data)
        # Tái tạo lại kiến trúc mạng nơ-ron
        net = tflearn.input_data(shape=[None, len(train_x[0])])
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
        net = tflearn.regression(net)
        # Tải trọng số (kiến thức) đã huấn luyện vào mô hình
        self.model = tflearn.DNN(net, tensorboard_dir=path.getPath('train_logs'))
        self.model.load(path.getPath('model.tflearn'))

    def clean_up_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [self.stemmer.stem(word.lower()) for word in sentence_words]
        return sentence_words

    def bow(self, sentence, words, show_details=False):
        sentence_words = self.clean_up_sentence(sentence)
        bag = [0] * len(words)
        for s in sentence_words:
            for i, w in enumerate(words):
                if w == s:
                    bag[i] = 1
                    if show_details:
                        print("found in bag: %s" % w)
        return np.array(bag)
    # Dự đoán ý định
    def classify(self, sentence):
        ERROR_THRESHOLD = 0.25
        results = self.model.predict([self.bow(sentence, self.words)])[0]
        results = [[i, r] for i, r in enumerate(results) if r > ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append((self.classes[r[0]], r[1]))
        return return_list
    # Logic cốt lõi của Chatbot
    def response(self, sentence, userID='111', show_details=False):
    # Classify the sentence to get a sorted list of intents
     results = self.classify(sentence)

    # Check if classification returned any results
     if results:
        # Loop through all results, not just the top one
        for intent_tag, probability in results:
            # Find the full intent details from our predefined list
            for i in self.intents['intents']:
                if i['tag'] == intent_tag:
                    
                    # --- Context Filtering Logic ---
                    # Check if this intent requires a context
                    has_context_filter = 'context_filter' in i
                    
                    # Check if the user's current context matches what the intent needs
                    # Note: We get the context from self.context now!
                    user_context = self.context.get(userID)
                    context_is_valid = user_context == i.get('context_filter')

                    # If the intent has no context filter, or if the context is valid...
                    if not has_context_filter or context_is_valid:
                        if show_details:
                            print('tag:', i['tag'])

                        # --- Context Setting Logic ---
                        # If this intent sets a new context, update it in self.context
                        if 'context_set' in i:
                            if show_details:
                                print('context set:', i['context_set'])
                            self.context[userID] = i['context_set']
                        # If the intent doesn't set a context, clear the user's old context
                        else:
                            self.context.pop(userID, None)
                            
                        # Return a random response
                        return random.choice(i['responses'])

    # Nếu không tìm thấy intent phù hợp, sử dụng logic thông minh hơn
     return self.smart_fallback_response(sentence, userID)

    def smart_fallback_response(self, sentence, userID='111'):
        """
        Xử lý các câu hỏi ngoài phạm vi training một cách thông minh
        """
        sentence_lower = sentence.lower()
        
        # Kiểm tra context trước đó để trả lời phù hợp
        user_context = self.context.get(userID, '')
        
        # Nếu đang trong context về một CLB cụ thể
        if user_context and any(clb in user_context.lower() for clb in ['real madrid', 'barcelona', 'manchester united', 'liverpool', 'psg', 'bayern']):
            if any(keyword in sentence_lower for keyword in ['giá', 'bao nhiêu', 'tiền', 'cost', 'price']):
                return f"Áo {user_context} có giá từ 350-450k tùy phiên bản (Fan/Player). Bạn muốn phiên bản nào?"
            elif any(keyword in sentence_lower for keyword in ['mua', 'đặt', 'order', 'purchase']):
                return f"Bạn muốn đặt áo {user_context} phải không? Mình có thể tư vấn size và phiên bản cho bạn!"
            elif any(keyword in sentence_lower for keyword in ['size', 'cỡ', 'vừa']):
                return f"Áo {user_context} có size S-XL. Bạn cao bao nhiêu để mình tư vấn size phù hợp?"
            elif any(keyword in sentence_lower for keyword in ['mới', 'new', '2024', '2025']):
                return f"Áo {user_context} mùa giải 2024-25 đã về! Giá từ 380-480k tùy phiên bản."
            elif any(keyword in sentence_lower for keyword in ['cũ', 'old', 'retro', 'vintage']):
                return f"Shop có áo {user_context} các mùa trước từ 2020-2023. Bạn muốn mùa nào?"
        
        # Kiểm tra các từ khóa liên quan đến bóng đá
        football_keywords = ['bóng đá', 'football', 'soccer', 'clb', 'đội tuyển', 'cầu thủ', 'sân', 'trận đấu']
        if any(keyword in sentence_lower for keyword in football_keywords):
            return "Mình hiểu bạn đang hỏi về bóng đá! Shop chuyên về áo bóng đá các CLB và đội tuyển. Bạn muốn tìm áo CLB nào cụ thể không?"
        
        # Kiểm tra các từ khóa về thời trang
        fashion_keywords = ['áo', 'quần', 'giày', 'mặc', 'thời trang', 'style']
        if any(keyword in sentence_lower for keyword in fashion_keywords):
            return "Shop chuyên về áo bóng đá chính hãng! Bạn có thể hỏi về áo CLB, áo tuyển quốc gia, hoặc phụ kiện bóng đá nhé!"
        
        # Kiểm tra các từ khóa về mua sắm
        shopping_keywords = ['mua', 'bán', 'giá', 'tiền', 'đặt hàng', 'thanh toán']
        if any(keyword in sentence_lower for keyword in shopping_keywords):
            return "Bạn muốn mua áo bóng đá phải không? Shop có đầy đủ áo các CLB lớn như Real Madrid, Barcelona, Manchester United... Bạn quan tâm CLB nào?"
        
        # Kiểm tra và lưu context về CLB cụ thể
        clb_keywords = {
            'real madrid': ['real madrid', 'real', 'madrid'],
            'barcelona': ['barcelona', 'barca', 'fc barcelona'],
            'manchester united': ['manchester united', 'man utd', 'mu', 'man united'],
            'liverpool': ['liverpool', 'lfc', 'liverpool fc'],
            'psg': ['psg', 'paris saint-germain', 'paris'],
            'bayern munich': ['bayern', 'bayern munich', 'bayern münchen']
        }
        
        # Kiểm tra và lưu context về đội tuyển quốc gia
        national_team_keywords = {
            'đội tuyển pháp': ['đội tuyển pháp', 'tuyển pháp', 'france', 'pháp'],
            'đội tuyển anh': ['đội tuyển anh', 'tuyển anh', 'england', 'anh'],
            'đội tuyển argentina': ['đội tuyển argentina', 'tuyển argentina', 'argentina'],
            'đội tuyển brazil': ['đội tuyển brazil', 'tuyển brazil', 'brazil'],
            'đội tuyển việt nam': ['đội tuyển việt nam', 'tuyển việt nam', 'vietnam'],
            'đội tuyển đức': ['đội tuyển đức', 'tuyển đức', 'germany', 'đức'],
            'đội tuyển tây ban nha': ['đội tuyển tây ban nha', 'tuyển tây ban nha', 'spain', 'tây ban nha']
        }
        
        # Kiểm tra đội tuyển quốc gia trước
        for team_name, keywords in national_team_keywords.items():
            if any(keyword in sentence_lower for keyword in keywords):
                # Lưu context về đội tuyển này
                self.context[userID] = team_name
                return f"Bạn quan tâm áo {team_name} phải không? Mình có áo chính thức của đội tuyển này! Giá từ 380-480k."
        
        # Kiểm tra CLB sau
        for clb_name, keywords in clb_keywords.items():
            if any(keyword in sentence_lower for keyword in keywords):
                # Lưu context về CLB này
                self.context[userID] = clb_name
                return f"Bạn quan tâm áo {clb_name} phải không? Mình có thể tư vấn về giá cả, size, phiên bản cho bạn!"
        
        # Kiểm tra các từ khóa về thể thao khác
        other_sports = ['bóng rổ', 'tennis', 'cầu lông', 'bơi lội', 'gym', 'fitness', 'bóng chuyền', 'bóng bàn', 'bơi', 'chạy']
        if any(sport in sentence_lower for sport in other_sports):
            return "Xin lỗi, shop chỉ chuyên về áo bóng đá thôi ạ! Mình có thể giúp bạn tìm áo CLB hoặc áo tuyển quốc gia nhé!"
        
        # Kiểm tra các câu hỏi cá nhân
        personal_keywords = ['tên', 'tuổi', 'ở đâu', 'làm gì', 'nghề nghiệp']
        if any(keyword in sentence_lower for keyword in personal_keywords):
            return "Mình là chatbot của shop áo bóng đá! Mình có thể giúp bạn tìm áo CLB, tư vấn size, giá cả, giao hàng... Bạn cần hỗ trợ gì?"
        
        # Kiểm tra các câu hỏi về thời tiết, tin tức
        news_keywords = ['thời tiết', 'tin tức', 'chính trị', 'kinh tế', 'covid']
        if any(keyword in sentence_lower for keyword in news_keywords):
            return "Mình chỉ biết về áo bóng đá thôi ạ! Bạn có thể hỏi mình về áo CLB, giá cả, size, hoặc cách đặt hàng nhé!"
        
        # Kiểm tra các câu hỏi về công nghệ
        tech_keywords = ['máy tính', 'điện thoại', 'app', 'website', 'internet', 'lập trình', 'code', 'phần mềm', 'hệ thống', 'database']
        if any(keyword in sentence_lower for keyword in tech_keywords):
            return "Shop chuyên về áo bóng đá, không bán đồ công nghệ ạ! Bạn muốn tìm áo CLB nào để mình tư vấn?"
        
        # Kiểm tra các câu hỏi về ẩm thực
        food_keywords = ['ăn', 'uống', 'nhà hàng', 'cafe', 'món ăn', 'thức ăn']
        if any(keyword in sentence_lower for keyword in food_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn xem mẫu nào không?"
        
        # Kiểm tra các câu hỏi về du lịch
        travel_keywords = ['du lịch', 'đi chơi', 'nghỉ mát', 'khách sạn', 'vé máy bay', 'resort', 'nghỉ dưỡng']
        if any(keyword in sentence_lower for keyword in travel_keywords):
            return "Shop chỉ bán áo bóng đá thôi ạ! Bạn có thể hỏi mình về áo CLB, áo tuyển quốc gia, hoặc phụ kiện bóng đá nhé!"
        
        # Kiểm tra các câu hỏi về giáo dục
        education_keywords = ['học', 'trường', 'sinh viên', 'bài tập', 'thi cử', 'sách', 'đọc', 'truyện', 'tiểu thuyết']
        if any(keyword in sentence_lower for keyword in education_keywords):
            return "Mình chỉ tư vấn về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về sức khỏe
        health_keywords = ['bệnh', 'thuốc', 'bác sĩ', 'sức khỏe', 'y tế', 'bệnh viện', 'y tá', 'khám']
        if any(keyword in sentence_lower for keyword in health_keywords):
            return "Mình chỉ biết về áo bóng đá thôi ạ! Bạn có thể hỏi mình về áo CLB, giá cả, size, hoặc cách đặt hàng nhé!"
        
        # Kiểm tra các câu hỏi về tình cảm
        relationship_keywords = ['yêu', 'thích', 'bạn gái', 'bạn trai', 'hôn nhân']
        if any(keyword in sentence_lower for keyword in relationship_keywords):
            return "Mình chỉ tư vấn về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào để tặng người yêu không?"
        
        # Kiểm tra các câu hỏi về công việc
        work_keywords = ['công việc', 'làm việc', 'lương', 'nghề', 'công ty']
        if any(keyword in sentence_lower for keyword in work_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về giải trí
        entertainment_keywords = ['phim', 'nhạc', 'game', 'ca sĩ', 'diễn viên']
        if any(keyword in sentence_lower for keyword in entertainment_keywords):
            return "Mình chỉ tư vấn về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về tài chính
        finance_keywords = ['tiền', 'ngân hàng', 'đầu tư', 'cổ phiếu', 'bitcoin', 'kinh tế', 'thị trường']
        if any(keyword in sentence_lower for keyword in finance_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về xe cộ
        vehicle_keywords = ['xe', 'ô tô', 'xe máy', 'xe đạp', 'giao thông', 'vận tải', 'tàu', 'máy bay']
        if any(keyword in sentence_lower for keyword in vehicle_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về nhà cửa
        house_keywords = ['nhà', 'căn hộ', 'mua nhà', 'thuê nhà', 'nội thất', 'xây dựng', 'công trình', 'kiến trúc', 'thiết kế']
        if any(keyword in sentence_lower for keyword in house_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về thú cưng
        pet_keywords = ['chó', 'mèo', 'thú cưng', 'nuôi', 'cún']
        if any(keyword in sentence_lower for keyword in pet_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về nghệ thuật
        art_keywords = ['vẽ', 'hội họa', 'âm nhạc', 'nghệ thuật', 'tranh']
        if any(keyword in sentence_lower for keyword in art_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về thời gian
        time_keywords = ['mấy giờ', 'thời gian', 'ngày', 'tháng', 'năm']
        if any(keyword in sentence_lower for keyword in time_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về địa lý
        geography_keywords = ['thành phố', 'quốc gia', 'châu lục', 'biển', 'núi']
        if any(keyword in sentence_lower for keyword in geography_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về lịch sử
        history_keywords = ['lịch sử', 'cổ đại', 'chiến tranh', 'vua', 'hoàng đế']
        if any(keyword in sentence_lower for keyword in history_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về khoa học
        science_keywords = ['khoa học', 'vật lý', 'hóa học', 'sinh học', 'toán']
        if any(keyword in sentence_lower for keyword in science_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về tôn giáo
        religion_keywords = ['tôn giáo', 'phật', 'chúa', 'thánh', 'thiên chúa']
        if any(keyword in sentence_lower for keyword in religion_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về chính trị
        politics_keywords = ['chính trị', 'tổng thống', 'thủ tướng', 'bầu cử', 'đảng']
        if any(keyword in sentence_lower for keyword in politics_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về môi trường
        environment_keywords = ['môi trường', 'ô nhiễm', 'khí hậu', 'nóng lên', 'xanh']
        if any(keyword in sentence_lower for keyword in environment_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về pháp luật
        law_keywords = ['luật', 'pháp luật', 'tòa án', 'luật sư', 'kiện']
        if any(keyword in sentence_lower for keyword in law_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về quân sự
        military_keywords = ['quân đội', 'quân sự', 'chiến tranh', 'vũ khí', 'bộ đội']
        if any(keyword in sentence_lower for keyword in military_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về nông nghiệp
        agriculture_keywords = ['nông nghiệp', 'trồng trọt', 'chăn nuôi', 'cây trồng', 'vật nuôi']
        if any(keyword in sentence_lower for keyword in agriculture_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về công nghiệp
        industry_keywords = ['công nghiệp', 'nhà máy', 'sản xuất', 'máy móc', 'thiết bị']
        if any(keyword in sentence_lower for keyword in industry_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về dịch vụ
        service_keywords = ['dịch vụ', 'phục vụ', 'chăm sóc', 'hỗ trợ', 'tư vấn']
        if any(keyword in sentence_lower for keyword in service_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về bưu chính
        postal_keywords = ['bưu chính', 'bưu điện', 'gửi thư', 'bưu phẩm', 'thư']
        if any(keyword in sentence_lower for keyword in postal_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về viễn thông
        telecom_keywords = ['viễn thông', 'điện thoại', 'internet', 'mạng', 'wifi']
        if any(keyword in sentence_lower for keyword in telecom_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Kiểm tra các câu hỏi về năng lượng
        energy_keywords = ['năng lượng', 'điện', 'dầu', 'khí', 'than']
        if any(keyword in sentence_lower for keyword in energy_keywords):
            return "Mình chỉ biết về áo bóng đá thôi! Shop có áo các CLB lớn, bạn muốn tìm áo nào?"
        
        # Nếu không tìm thấy từ khóa nào, trả về câu trả lời mặc định thông minh hơn
        return "Xin lỗi, mình chưa hiểu câu hỏi của bạn. Mình chỉ biết về áo bóng đá thôi! Bạn có thể hỏi mình về:\n- Áo CLB (Real Madrid, Barcelona, Manchester United...)\n- Áo tuyển quốc gia\n- Giá cả và size\n- Giao hàng và thanh toán\n- Phụ kiện bóng đá\nBạn muốn hỏi gì cụ thể?"