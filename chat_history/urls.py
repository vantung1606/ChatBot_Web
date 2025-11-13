from django.urls import path
from . import views

urlpatterns = [
    # Đường dẫn gốc của app, trỏ đến view history_list
    path('', views.history_list, name='history_list'),
]