import os
import django

# --- Cấu hình môi trường Django (Rất quan trọng) ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CHATBOT_WEB.settings')
django.setup()

import nltk
import numpy as np
import tensorflow as tf
import tflearn
import random
import pickle
from Bot import path

# ✅ BƯỚC 1: IMPORT CÁC HÀM TỪ FILE THU THẬP DỮ LIỆU
# Chúng ta sẽ coi `thuthapdulieu.py` như một module và lấy các hàm cần thiết
from Bot.thuthapdulieu import crawl_local_shop, products_to_intents, sync_intents_to_db

from intent_manager.models import Intent, Pattern # Lấy dữ liệu từ model

# --- TỰ ĐỘNG CHẠY QUÁ TRÌNH THU THẬP DỮ LIỆU TRƯỚC KHI HUẤN LUYỆN ---
print("\n" + "="*50)
print("BƯỚC 1: TỰ ĐỘNG THU THẬP VÀ CẬP NHẬT DỮ LIỆU SẢN PHẨM")
print("="*50)
products = crawl_local_shop()
if products:
    new_intents = products_to_intents(products)
    sync_intents_to_db(new_intents)
else:
    print("CẢNH BÁO: Không cào được sản phẩm nào. Tiếp tục huấn luyện với dữ liệu cũ.")

print("Đang lấy dữ liệu intents từ database...")
# ✅ THAY ĐỔI LỚN: Không đọc từ file JSON nữa, mà truy vấn thẳng từ database
intents_from_db = Intent.objects.prefetch_related('patterns', 'responses').all()
if not intents_from_db:
    print("LỖI: Không tìm thấy intent nào trong database. Bạn đã chạy file thuthapdulieu.py để thêm vào database chưa?")
    exit()
print(f"Đã lấy thành công {len(intents_from_db)} intents.")

words = []
# nhãn
classes = []
# danh sách các mẫu câu, cùng với nhãn tương ứng
documents = []
ignore_words = ['?']

for intent in intents_from_db:
    for pattern in intent.patterns.all():
        # tách từ
        w = nltk.word_tokenize(pattern.text)
        # thêm vào danh sách từ
        words.extend(w)
        documents.append((w, intent.tag))
    if intent.tag not in classes:
        classes.append(intent.tag)

# ✅ THAY ĐỔI: Chỉ chuyển về chữ thường, không dùng stemmer nữa
words = [w.lower() for w in words if w not in ignore_words]
words = sorted(list(set(words)))

classes = sorted(list(set(classes)))

print(len(documents), "Docs")
print(len(classes), "Classes", classes)
print(len(words), "Split words", words)

# tạo dữ liệu huấn luyện
training = []
training_x = []
training_y = []
output_empty = [0] * len(classes)

for doc in documents:
    bag = []
    pattern_words = doc[0]
    pattern_words = [word.lower() for word in pattern_words] # ✅ THAY ĐỔI: Chỉ chuyển về chữ thường
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)

    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1

    training_x.append(bag)
    training_y.append(output_row)

train_x = np.array(training_x)
train_y = np.array(training_y)


# xây dựng mô hình
# reset đồ thị mặc định
tf.compat.v1.reset_default_graph()
# nhập lớp dữ liệu
net = tflearn.input_data(shape=[None, len(train_x[0])])
# bộ não 2 lớp 8 neuron (deepening the network)
net = tflearn.fully_connected(net, 16) # Tăng số nơ-ron (lớp ẩn)
net = tflearn.fully_connected(net, 16) # Tăng số nơ-ron
# lớp đầu ra với hàm kích hoạt softmax
net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
net = tflearn.regression(net)
# khởi tạo mô hình
model = tflearn.DNN(net, tensorboard_dir=path.getPath('train_logs'))
# huấn luyện mô hình
model.fit(train_x, train_y, n_epoch=1000, batch_size=8, show_metric=True) # Giảm epoch, giảm batch_size
model.save(path.getPath('model.tflearn'))

# hàm tiền xử lý câu y hệt
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [word.lower() for word in sentence_words] # ✅ THAY ĐỔI: Chỉ chuyển về chữ thường
    return sentence_words


def bow(sentence, words, show_details=False):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)


pickle.dump({'words': words, 'classes': classes, 'train_x': train_x, 'train_y': train_y},
            open(path.getPath('trained_data'), "wb"))
