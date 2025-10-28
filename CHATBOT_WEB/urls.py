from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index),
    path('api', include("CHATBOT_WEB.Api.urls")),
     # Thêm dòng này:
    path('api/chat/', views.chat_api, name='chat_api'), 
    # Bạn cũng có thể cần một path để hiển thị trang chat
    # path('', views.chat_page, name='chat_page'), # Sẽ tạo ở bước sau
]
