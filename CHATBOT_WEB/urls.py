from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    # ✅ THÊM DÒNG NÀY: Khai báo đường dẫn cho trang quản trị
    path('admin/', admin.site.urls),

    # ✅ THÊM DÒNG NÀY: Đường dẫn đến trang xem lịch sử chat
    # Nó sẽ tìm các URL con trong file `chat_history.urls`
    path('history/', include('chat_history.urls')),

    # Đường dẫn đến trang chat chính
    path('', views.index, name='index'),
    # Đường dẫn API để xử lý tin nhắn
    path('api/chat/', views.chat_api, name='chat_api'), 
]
