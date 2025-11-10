from django.contrib import admin
from .models import Intent, Pattern, Response

# Cho phép sửa Pattern ngay trên trang Intent
class PatternInline(admin.TabularInline):
    model = Pattern
    extra = 1 # Hiển thị 1 ô trống để thêm mới

# Cho phép sửa Response ngay trên trang Intent
class ResponseInline(admin.TabularInline):
    model = Response
    extra = 1 # Hiển thị 1 ô trống để thêm mới

@admin.register(Intent)
class IntentAdmin(admin.ModelAdmin):
    list_display = ('tag', 'product_page_url')
    search_fields = ('tag',)
    # Gắn các form inline vào trang admin của Intent
    inlines = [PatternInline, ResponseInline]

# Đăng ký riêng để có thể quản lý tập trung (tùy chọn)
# admin.site.register(Pattern)
# admin.site.register(Response)
