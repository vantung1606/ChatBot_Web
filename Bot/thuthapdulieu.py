import os
import django
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# --- Cấu hình môi trường Django (Rất quan trọng) ---
# Giúp script này có thể truy cập và sử dụng các model của Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CHATBOT_WEB.settings')
django.setup()
# --- Kết thúc cấu hình ---

from intent_manager.models import Intent, Pattern, Response # ✅ Lấy dữ liệu từ model

# Bắt buộc hiển thị Unicode đúng trên Windows
sys.stdout.reconfigure(encoding='utf-8')

# Gán URL trực tiếp
base_url = "http://localhost:8080/IndexController/"

def crawl_local_shop(url=base_url):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"LỖI: Không thể kết nối tới {url}.")
        print("Gợi ý: Bạn đã chạy server Java chứa trang web bán hàng chưa?")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    products = []
    
    product_elements = soup.select(".productinfo")
    
    if not product_elements:
        print("CẢNH BÁO: Không tìm thấy sản phẩm nào với class '.productinfo'")
        return []

    print(f"Tìm thấy {len(product_elements)} sản phẩm, đang xử lý...")

    for item in product_elements:
        try:
            price_tag = item.select_one("h2")
            title_tag = item.select_one("p")
            img_tag = item.select_one("img")
            link_tag = item.select_one("a.add-to-cart")
            
            if not link_tag:
                link_tag = item.select_one("p a")
            
            if not link_tag:
                img_parent_link = img_tag.find_parent("a")
                if img_parent_link:
                    link_tag = img_parent_link

            if not (title_tag and price_tag and img_tag and link_tag):
                print("Bỏ qua 1 sản phẩm bị thiếu (thiếu h2, p, img, hoặc thẻ <a>)")
                continue

            title = title_tag.text.strip()
            price = price_tag.text.strip()
            relative_url = link_tag.get("href")
            product_page_url = urljoin(url, relative_url)

            products.append({
                "title": title,
                "price": price,
                "product_page_url": product_page_url
            })
        except Exception as e:
            print(f"Lỗi khi xử lý 1 sản phẩm: {e}")
            
    print(f"Đã cào thành công {len(products)} sản phẩm.")
    return products

def products_to_intents(products):
    # Hàm này giữ nguyên logic tạo intents từ sản phẩm
    intents = []
    for prod in products:
        tag = prod["title"].lower().replace(" ", "_").replace("-", "_").replace("'", "").replace("/", "_")
        tag = f"prod_{tag}"

        keyword_map = {
            "manchester united": ["mu", "man united", "man utd", "quỷ đỏ"],
            "barcelona": ["barca", "fcb", "blaugrana"],
            "real madrid": ["real", "kền kền trắng", "los blancos"]
        }

        keywords = []
        for main_name, aliases in keyword_map.items():
            if main_name in prod['title'].lower():
                keywords.extend(aliases)
                keywords.append(main_name)
                break

        if not keywords:
            keywords.append(prod['title'])
        keywords = list(set(keywords))

        patterns = [f"{kw} giá bao nhiêu?" for kw in keywords] + \
                   [f"cho mình xem {kw}" for kw in keywords] + \
                   [f"shop có {kw} không" for kw in keywords] + \
                   [f"mua {kw}" for kw in keywords] + \
                   [f"chi tiết {kw}" for kw in keywords]
        
        responses = [
            f"{prod['title']} hiện tại giá {prod['price']}. Bạn có thể xem chi tiết ở link bên dưới.",
            f"Dạ có, {prod['title']} giá {prod['price']}. Bạn bấm vào link để xem chi tiết và đặt hàng nhé!"
        ]
        
        intents.append({
            "tag": tag,
            "patterns": patterns,
            "responses": responses,
            "product_page_url": prod["product_page_url"]
        })
    return intents

# ✅ HÀM ĐÃ ĐƯỢC NÂNG CẤP ĐỂ GHI VÀO DATABASE
def sync_intents_to_db(new_intents):
    """
    Đồng bộ hóa danh sách intents vào database.
    - Nếu intent chưa có, tạo mới.
    - Nếu intent đã có, cập nhật và làm mới patterns/responses.
    """
    print("Bắt đầu đồng bộ hóa intents vào database...")
    count_new = 0
    count_updated = 0

    for intent_data in new_intents:
        tag = intent_data['tag']
        
        # Sử dụng get_or_create để vừa tìm, vừa tạo nếu chưa có
        intent_obj, created = Intent.objects.get_or_create(
            tag=tag,
            defaults={'product_page_url': intent_data['product_page_url']}
        )

        if created:
            # Nếu là intent mới được tạo
            count_new += 1
            print(f"   -> Tạo mới intent: '{tag}'")
        else:
            # Nếu intent đã tồn tại, cập nhật link và xóa các pattern/response cũ
            intent_obj.product_page_url = intent_data['product_page_url']
            intent_obj.save()
            intent_obj.patterns.all().delete()
            intent_obj.responses.all().delete()
            count_updated += 1
            print(f"   -> Cập nhật intent: '{tag}'")
        
        # Thêm các pattern và response mới (dùng bulk_create để tối ưu hiệu suất)
        patterns_to_create = [Pattern(intent=intent_obj, text=p) for p in intent_data['patterns']]
        Pattern.objects.bulk_create(patterns_to_create)
        
        responses_to_create = [Response(intent=intent_obj, text=r) for r in intent_data['responses']]
        Response.objects.bulk_create(responses_to_create)

    print("-" * 20)
    print(f"Đã thêm {count_new} sản phẩm mới vào database.")
    print(f"Đã cập nhật {count_updated} sản phẩm cũ trong database.")
    print("✅ Đồng bộ hóa hoàn tất!")

# --- Main ---
if __name__ == "__main__":
    products = crawl_local_shop()
    if products: 
        new_intents = products_to_intents(products)
        sync_intents_to_db(new_intents) # ✅ Gọi hàm mới để ghi vào DB
    else:
        print("Không cào được sản phẩm nào. Dừng chương trình.")