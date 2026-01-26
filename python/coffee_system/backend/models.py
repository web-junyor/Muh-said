#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Models for Coffee Shop Management System
Loveble integratsiyasi bilan mahsulot, sotuvlar va diagnostika modellar
"""

from pydantic import BaseModel
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List
import json


# ==================== Pydantic Models ====================

class ClickPayment(BaseModel):
    """Click payment model"""
    merchant_trans_id: str
    amount: int
    sign_time: str
    sign_string: str
    status: int


class LovebleOrderItem(BaseModel):
    """Loveble buyurtmadagi bir dona mahsulot"""
    product_id: str
    product_name: str
    quantity: int
    price: int  # har bir dona uchun
    total_price: int  # jami


class LovebleWebhookPayload(BaseModel):
    """Loveble webhookdan keladigan payload"""
    event_type: str  # 'order_created', 'order_paid', 'order_completed'
    order_id: str
    shop_id: str
    timestamp: str
    items: List[LovebleOrderItem]
    total_amount: int
    payment_status: str
    payment_method: Optional[str] = "cash"
    customer_phone: Optional[str] = None


# ==================== Dataclass Models ====================

@dataclass
class Product:
    """Mahsulot modeli"""
    id: str
    name: str
    price: int  # som
    current_stock: int
    initial_stock: int
    loveble_id: str
    created_at: str = None
    updated_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return Product(**data)

    def is_low_stock(self, threshold: int) -> bool:
        """Qoldig'i kam ekanini tekshirish"""
        return self.current_stock <= threshold

    def decrease_stock(self, quantity: int) -> bool:
        """Qoldig'ini kamaytirish"""
        if self.current_stock >= quantity:
            self.current_stock -= quantity
            self.updated_at = datetime.now().isoformat()
            return True
        return False

    def increase_stock(self, quantity: int):
        """Qoldig'ini oshirish"""
        self.current_stock += quantity
        self.updated_at = datetime.now().isoformat()


@dataclass
class Sale:
    """Sotuvlar haqida ma'lumot"""
    id: str
    product_id: str
    product_name: str
    quantity: int
    price: int  # har bir dona uchun
    total_price: int  # jami narx
    check_id: str  # Loveble chek ID
    timestamp: str
    loveble_order_id: str
    payment_method: str = "cash"
    status: str = "completed"

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return Sale(**data)


@dataclass
class DailyReport:
    """Kunlik diagnostika hisoboti"""
    date: str
    total_sales: int  # jami sotuvlar soni
    total_revenue: int  # jami daromad (som)
    products_sold: dict  # {product_name: quantity}
    stock_levels: dict  # {product_name: remaining_stock}
    low_stock_products: List[str]
    report_time: str

    def __post_init__(self):
        if self.report_time is None:
            self.report_time = datetime.now().isoformat()

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return DailyReport(**data)


@dataclass
class WeeklyReport:
    """Haftalik diagnostika hisoboti"""
    week_number: int
    year: int
    total_sales: int
    total_revenue: int
    products_sold: dict
    average_daily_sales: float
    best_selling_product: str
    worst_selling_product: str
    stock_efficiency: float
    report_time: str

    def __post_init__(self):
        if self.report_time is None:
            self.report_time = datetime.now().isoformat()

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return WeeklyReport(**data)


@dataclass
class MonthlyReport:
    """Oylik diagnostika hisoboti"""
    month: int
    year: int
    total_sales: int
    total_revenue: int
    products_sold: dict
    average_daily_sales: float
    average_daily_revenue: int
    best_selling_product: str
    worst_selling_product: str
    most_profitable_product: str
    stock_efficiency: float
    growth_percentage: float
    report_time: str

    def __post_init__(self):
        if self.report_time is None:
            self.report_time = datetime.now().isoformat()

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return MonthlyReport(**data)


@dataclass
class LovebleWebhookData:
    """Loveble webhookdan keladigan ma'lumot"""
    event_type: str
    order_id: str
    shop_id: str
    timestamp: str
    order_data: dict
    items: List[dict]
    total_amount: int
    payment_status: str
    customer_info: Optional[dict] = None

    @staticmethod
    def from_dict(data):
        return LovebleWebhookData(**data)

    def to_dict(self):
        return asdict(self)


@dataclass
class StockSnapshot:
    """Inventar holati surat olish"""
    timestamp: str
    products: dict  # {product_name: quantity}

    @property
    def total_items(self) -> int:
        return sum(self.products.values())

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "products": self.products,
            "total_items": self.total_items
        }

    @staticmethod
    def from_dict(data):
        return StockSnapshot(data['timestamp'], data['products'])
