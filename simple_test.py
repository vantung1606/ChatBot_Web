# Test đơn giản cho ChatBot
import sys
sys.path.append('.')

try:
    from Bot.ChatBot import ChatBot
    print("✅ Import ChatBot thành công!")
    
    bot = ChatBot.getBot()
    print("✅ Khởi tạo ChatBot thành công!")
    
    # Test cơ bản
    print("\n=== TEST CƠ BẢN ===")
    
    print("1. Hi:", bot.response('Hi'))
    print("2. Đội tuyển Pháp:", bot.response('đội tuyển pháp'))
    print("3. Real Madrid:", bot.response('Real Madrid'))
    print("4. Giá:", bot.response('giá'))
    print("5. Thời tiết:", bot.response('Thời tiết hôm nay thế nào?'))
    
    print("\n✅ Test hoàn thành!")
    
except Exception as e:
    print(f"❌ Lỗi: {e}")
    import traceback
    traceback.print_exc()

