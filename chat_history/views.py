from django.shortcuts import render
from .models import ChatHistory

def history_list(request):
    """
    View này lấy tất cả lịch sử chat từ database và hiển thị ra template.
    """
    # Truy vấn tất cả các đối tượng ChatHistory, sắp xếp theo thời gian giảm dần
    chat_sessions = ChatHistory.objects.all().order_by('-timestamp')
    
    # Dữ liệu để truyền sang template
    context = {
        'chat_sessions': chat_sessions
    }
    return render(request, 'chat_history/history_list.html', context)
