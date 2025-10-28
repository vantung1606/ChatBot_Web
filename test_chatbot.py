#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script cho ChatBot với logic từ khóa thông minh
"""

import sys
import os
sys.path.append('.')

from Bot.ChatBot import ChatBot

def test_chatbot():
    print("🚀 Khởi tạo ChatBot...")
    bot = ChatBot.getBot()
    
    print("\n=== TEST CHATBOT VỚI LOGIC TỪ KHÓA THÔNG MINH ===")
    
    # Test đội tuyển quốc gia
    print("\n1. Đội tuyển Pháp:")
    response = bot.response('đội tuyển pháp')
    print(f"   → {response}")
    
    print("\n2. Giá áo Pháp:")
    response = bot.response('giá')
    print(f"   → {response}")
    
    print("\n3. Mua áo Pháp:")
    response = bot.response('mua')
    print(f"   → {response}")
    
    # Test CLB
    print("\n4. Real Madrid:")
    response = bot.response('Real Madrid')
    print(f"   → {response}")
    
    print("\n5. Giá Real:")
    response = bot.response('giá')
    print(f"   → {response}")
    
    # Test câu hỏi ngoài phạm vi
    print("\n6. Câu hỏi ngoài phạm vi:")
    response = bot.response('Thời tiết hôm nay thế nào?')
    print(f"   → {response}")
    
    print("\n7. Câu hỏi công nghệ:")
    response = bot.response('Lập trình Python như thế nào?')
    print(f"   → {response}")
    
    print("\n8. Câu hỏi ẩm thực:")
    response = bot.response('Món phở ngon ở đâu?')
    print(f"   → {response}")
    
    print("\n✅ Test hoàn thành!")

if __name__ == "__main__":
    test_chatbot()
