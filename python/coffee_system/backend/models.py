from pydantic import BaseModel
from typing import List


class ItemModel(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: int
    total_price: int


class OrderPaid(BaseModel):
    order_id: str
    merchant_trans_id: str
    payment_status: str
    items: List[ItemModel]
    total_amount: int
    sign_string: str
    sign_time: str
