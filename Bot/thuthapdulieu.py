import os
import django
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CHATBOT_WEB.settings')
django.setup()

from intent_manager.models import Intent, Pattern, Response

sys.stdout.reconfigure(encoding='utf-8')

base_url = "http://localhost:8080/IndexController/"

def crawl_local_shop(url=base_url):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Lỗi: Không thể kết nối tới {url}. Đã chạy server Java chưa?")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    products = []
    product_elements = soup.select(".productinfo")

    if not product_elements:
        print("Không tìm thấy sản phẩm nào.")
        return []

    for item in product_elements:
        try:
            price_tag = item.select_one("h2")
            title_tag = item.select_one("p")
            img_tag = item.select_one("img")
            link_tag = item.select_one("a.add-to-cart") or item.select_one("p a") or (img_tag.find_parent("a") if img_tag else None)

            if not all([title_tag, price_tag, img_tag, link_tag]):
                continue

            title = title_tag.text.strip()
            price = price_tag.text.strip()
            product_page_url = urljoin(url, link_tag.get("href"))

            products.append({
                "title": title,
                "price": price,
                "product_page_url": product_page_url
            })
        except Exception as e:
            print(f"Lỗi xử lý sản phẩm: {e}")

    print(f"Đã cào {len(products)} sản phẩm.")
    return products

def products_to_intents(products):
    intents = []
    for prod in products:
        title_clean = prod['title'].lower().replace(' ', '_').replace('-', '_').replace("'", '').replace('/', '_')
        tag = f"prod_{title_clean}"

        keyword_map = {
            "manchester united": ["mu", "man united", "man utd", "quỷ đỏ"],
            "barcelona": ["barca", "fcb", "blaugrana"],
            "real madrid": ["real", "kền kền trắng", "los blancos"]
        }

        keywords = []
        for main_name, aliases in keyword_map.items():
            if main_name in prod['title'].lower():
                keywords.extend(aliases + [main_name])
                break
        else:
            keywords = [prod['title']]

        keywords = list(set(keywords))
        patterns = [f"{kw} giá bao nhiêu?" for kw in keywords] + [f"cho mình xem {kw}" for kw in keywords] + [f"shop có {kw} không" for kw in keywords] + [f"mua {kw}" for kw in keywords] + [f"chi tiết {kw}" for kw in keywords]
        responses = [f"{prod['title']} hiện tại giá {prod['price']}. Bạn có thể xem chi tiết ở link bên dưới.", f"Dạ có, {prod['title']} giá {prod['price']}. Bạn bấm vào link để xem chi tiết và đặt hàng nhé!"]

        intents.append({
            "tag": tag,
            "patterns": patterns,
            "responses": responses,
            "product_page_url": prod["product_page_url"]
        })
    return intents

def sync_intents_to_db(new_intents):
    print("Đồng bộ intents vào DB...")
    count_new = 0
    count_updated = 0

    for intent_data in new_intents:
        tag = intent_data['tag']
        intent_obj, created = Intent.objects.get_or_create(
            tag=tag,
            defaults={'product_page_url': intent_data['product_page_url']}
        )

        if created:
            count_new += 1
        else:
            intent_obj.product_page_url = intent_data['product_page_url']
            intent_obj.save()
            intent_obj.patterns.all().delete()
            intent_obj.responses.all().delete()
            count_updated += 1

        Pattern.objects.bulk_create([Pattern(intent=intent_obj, text=p) for p in intent_data['patterns']])
        Response.objects.bulk_create([Response(intent=intent_obj, text=r) for r in intent_data['responses']])

    print(f"Thêm {count_new} mới, cập nhật {count_updated} cũ. Hoàn tất!")

# --- Main ---
if __name__ == "__main__":
    products = crawl_local_shop()
    if products: 
        new_intents = products_to_intents(products)
        sync_intents_to_db(new_intents)
    else:
        print("Không cào được sản phẩm nào. Dừng chương trình.")