from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    # ✅ THÊM DÒNG NÀY: Khai báo đường dẫn cho trang quản trị
    path('admin/', admin.site.urls),



    # Đường dẫn đến trang chat chính
    path('', views.index, name='index'),
    # Đường dẫn API để xử lý tin nhắn
    path('api/chat/', views.chat_api, name='chat_api'), 
]
