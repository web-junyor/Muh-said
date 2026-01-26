from backend.database import get_today_sales, get_stock

def build_daily_report() -> str:
    sales = get_today_sales()
    text = "📊 Kunlik diagnostika:\n\n"

    for product, qty in sales:
        left = get_stock(product)
        text += f"{product}: {qty} ta sotildi | Qoldi: {left}\n"

    return text
