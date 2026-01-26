#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Manager for Coffee Shop System
SQLite database bilan ishlash va inventarni boshqarish
"""

import sqlite3
import json
import os
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Tuple
from pathlib import Path
import logging

from config import (
    DATABASE_PATH, PRODUCTS, TIMEZONE,
    LOW_STOCK_THRESHOLD, CRITICAL_STOCK_THRESHOLD
)
from backend.models import Product, Sale, DailyReport, WeeklyReport, MonthlyReport

# Logging setup
logger = logging.getLogger(__name__)


class DatabaseManager:
    """SQLite database bilan ishlash"""

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.init_database()

    def init_database(self):
        """Database tablalarini yaratish"""
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()

            # Products table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    initial_stock INTEGER NOT NULL,
                    current_stock INTEGER NOT NULL,
                    price INTEGER NOT NULL,
                    loveble_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Sales table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    id TEXT PRIMARY KEY,
                    product_id TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price INTEGER NOT NULL,
                    total_price INTEGER NOT NULL,
                    check_id TEXT NOT NULL,
                    loveble_order_id TEXT,
                    payment_method TEXT DEFAULT 'cash',
                    status TEXT DEFAULT 'completed',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)

            # Stock snapshots (kunlik, haftalik, oylik)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_date DATE NOT NULL,
                    snapshot_type TEXT NOT NULL,
                    snapshot_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Daily reports
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL UNIQUE,
                    total_sales INTEGER NOT NULL,
                    total_revenue INTEGER NOT NULL,
                    products_sold TEXT NOT NULL,
                    stock_levels TEXT NOT NULL,
                    low_stock_products TEXT,
                    report_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Weekly reports
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS weekly_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    week_number INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    total_sales INTEGER NOT NULL,
                    total_revenue INTEGER NOT NULL,
                    products_sold TEXT NOT NULL,
                    report_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(week_number, year)
                )
            """)

            # Monthly reports
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS monthly_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    month INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    total_sales INTEGER NOT NULL,
                    total_revenue INTEGER NOT NULL,
                    products_sold TEXT NOT NULL,
                    report_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(month, year)
                )
            """)

            # Loveble webhook log
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS loveble_webhooks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    order_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    status TEXT DEFAULT 'processed',
                    error_message TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.connection.commit()

            # Mahsulotlarni initialize qilish
            self._initialize_products()

            logger.info("Database initialized successfully")

        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def _initialize_products(self):
        """Barcha mahsulotlarni initial qoldig'i bilan kiritish"""
        try:
            # Mavjud mahsulotlarni tekshirish
            self.cursor.execute("SELECT COUNT(*) FROM products")
            count = self.cursor.fetchone()[0]

            if count == 0:
                # Yangi mahsulotlarni kiritish
                for product_key, product_data in PRODUCTS.items():
                    self.cursor.execute(
                        """
                        INSERT OR IGNORE INTO products
                        (id, name, initial_stock, current_stock, price, loveble_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            product_data["id"],
                            product_data["name"],
                            product_data["initial_stock"],
                            product_data["initial_stock"],
                            product_data["price"],
                            product_data["loveble_id"]
                        )
                    )
                self.connection.commit()
                logger.info("Products initialized successfully")

        except sqlite3.Error as e:
            logger.error(f"Error initializing products: {e}")
            raise

    def get_all_products(self) -> List[Product]:
        """Barcha mahsulotlarni olish"""
        try:
            self.cursor.execute("SELECT * FROM products")
            rows = self.cursor.fetchall()
            products = []
            for row in rows:
                product = Product(
                    id=row["id"],
                    name=row["name"],
                    price=row["price"],
                    current_stock=row["current_stock"],
                    initial_stock=row["initial_stock"],
                    loveble_id=row["loveble_id"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
                products.append(product)
            return products
        except sqlite3.Error as e:
            logger.error(f"Error getting products: {e}")
            return []

    def get_product(self, product_name: str) -> Optional[Product]:
        """Alohida mahsulotni olish"""
        try:
            self.cursor.execute("SELECT * FROM products WHERE name = ?", (product_name,))
            row = self.cursor.fetchone()
            if row:
                return Product(
                    id=row["id"],
                    name=row["name"],
                    price=row["price"],
                    current_stock=row["current_stock"],
                    initial_stock=row["initial_stock"],
                    loveble_id=row["loveble_id"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
            return None
        except sqlite3.Error as e:
            logger.error(f"Error getting product: {e}")
            return None

    def register_sale(self, sale: Sale) -> bool:
        """Sotuvni qaydda olish"""
        try:
            # Sotuvni jadvalga kiritish
            self.cursor.execute(
                """
                INSERT INTO sales
                (id, product_id, product_name, quantity, price, total_price,
                 check_id, loveble_order_id, payment_method, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sale.id,
                    sale.product_id,
                    sale.product_name,
                    sale.quantity,
                    sale.price,
                    sale.total_price,
                    sale.check_id,
                    sale.loveble_order_id,
                    sale.payment_method,
                    sale.status,
                    sale.timestamp
                )
            )

            # Mahsulot qoldig'ini kamaytirish
            self.cursor.execute(
                "UPDATE products SET current_stock = current_stock - ? WHERE name = ?",
                (sale.quantity, sale.product_name)
            )

            self.connection.commit()
            logger.info(f"Sale registered: {sale.product_name} x{sale.quantity}")
            return True

        except sqlite3.Error as e:
            logger.error(f"Error registering sale: {e}")
            self.connection.rollback()
            return False

    def get_stock_level(self, product_name: str) -> Optional[int]:
        """Mahsulotning qoldig'i"""
        try:
            self.cursor.execute("SELECT current_stock FROM products WHERE name = ?", (product_name,))
            row = self.cursor.fetchone()
            return row[0] if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting stock level: {e}")
            return None

    def get_all_stock_levels(self) -> Dict[str, int]:
        """Barcha mahsulotlarning qoldig'i"""
        try:
            self.cursor.execute("SELECT name, current_stock FROM products")
            rows = self.cursor.fetchall()
            return {row[0]: row[1] for row in rows}
        except sqlite3.Error as e:
            logger.error(f"Error getting stock levels: {e}")
            return {}

    def get_low_stock_products(self, threshold: int = LOW_STOCK_THRESHOLD) -> List[str]:
        """Kam qoldig'i mahsulotlar"""
        try:
            self.cursor.execute(
                "SELECT name FROM products WHERE current_stock <= ?",
                (threshold,)
            )
            rows = self.cursor.fetchall()
            return [row[0] for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting low stock products: {e}")
            return []

    def get_sales_by_date(self, date_obj: date) -> List[Sale]:
        """Shu kungi sotuvlar"""
        try:
            date_str = date_obj.isoformat()
            self.cursor.execute(
                "SELECT * FROM sales WHERE DATE(timestamp) = ?",
                (date_str,)
            )
            rows = self.cursor.fetchall()
            sales = []
            for row in rows:
                sale = Sale(
                    id=row["id"],
                    product_id=row["product_id"],
                    product_name=row["product_name"],
                    quantity=row["quantity"],
                    price=row["price"],
                    total_price=row["total_price"],
                    check_id=row["check_id"],
                    loveble_order_id=row["loveble_order_id"],
                    payment_method=row["payment_method"],
                    status=row["status"],
                    timestamp=row["timestamp"]
                )
                sales.append(sale)
            return sales
        except sqlite3.Error as e:
            logger.error(f"Error getting sales by date: {e}")
            return []

    def get_sales_by_product(self, product_name: str, start_date: date = None, end_date: date = None) -> List[Sale]:
        """Mahsulot bo'yicha sotuvlar"""
        try:
            if start_date is None:
                start_date = date.today() - timedelta(days=30)
            if end_date is None:
                end_date = date.today()

            self.cursor.execute(
                """
                SELECT * FROM sales
                WHERE product_name = ? AND DATE(timestamp) BETWEEN ? AND ?
                ORDER BY timestamp DESC
                """,
                (product_name, start_date.isoformat(), end_date.isoformat())
            )
            rows = self.cursor.fetchall()
            sales = []
            for row in rows:
                sale = Sale(
                    id=row["id"],
                    product_id=row["product_id"],
                    product_name=row["product_name"],
                    quantity=row["quantity"],
                    price=row["price"],
                    total_price=row["total_price"],
                    check_id=row["check_id"],
                    loveble_order_id=row["loveble_order_id"],
                    payment_method=row["payment_method"],
                    status=row["status"],
                    timestamp=row["timestamp"]
                )
                sales.append(sale)
            return sales
        except sqlite3.Error as e:
            logger.error(f"Error getting sales by product: {e}")
            return []

    def save_daily_report(self, report: DailyReport) -> bool:
        """Kunlik hisobotni saqlash"""
        try:
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO daily_reports
                (date, total_sales, total_revenue, products_sold, stock_levels,
                 low_stock_products, report_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report.date,
                    report.total_sales,
                    report.total_revenue,
                    json.dumps(report.products_sold),
                    json.dumps(report.stock_levels),
                    json.dumps(report.low_stock_products),
                    json.dumps(report.to_dict())
                )
            )
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error saving daily report: {e}")
            return False

    def save_weekly_report(self, report: WeeklyReport) -> bool:
        """Haftalik hisobotni saqlash"""
        try:
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO weekly_reports
                (week_number, year, total_sales, total_revenue, products_sold, report_data)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    report.week_number,
                    report.year,
                    report.total_sales,
                    report.total_revenue,
                    json.dumps(report.products_sold),
                    json.dumps(report.to_dict())
                )
            )
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error saving weekly report: {e}")
            return False

    def save_monthly_report(self, report: MonthlyReport) -> bool:
        """Oylik hisobotni saqlash"""
        try:
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO monthly_reports
                (month, year, total_sales, total_revenue, products_sold, report_data)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    report.month,
                    report.year,
                    report.total_sales,
                    report.total_revenue,
                    json.dumps(report.products_sold),
                    json.dumps(report.to_dict())
                )
            )
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error saving monthly report: {e}")
            return False

    def log_webhook(self, event_type: str, order_id: str, payload: dict, status: str = "processed", error_msg: str = None) -> bool:
        """Loveble webhookni log qilish"""
        try:
            self.cursor.execute(
                """
                INSERT INTO loveble_webhooks (event_type, order_id, payload, status, error_message)
                VALUES (?, ?, ?, ?, ?)
                """,
                (event_type, order_id, json.dumps(payload), status, error_msg)
            )
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error logging webhook: {e}")
            return False

    def close(self):
        """Database ulanishni yopish"""
        try:
            if self.connection:
                self.connection.close()
                logger.info("Database connection closed")
        except sqlite3.Error as e:
            logger.error(f"Error closing database: {e}")


# Global database instance
db = DatabaseManager()


def get_today_sales():
    cursor.execute("""
        SELECT product, SUM(quantity)
        FROM sales
        WHERE created_at = date('now')
        GROUP BY product
    """)
    return cursor.fetchall()


def get_stock(product: str) -> int:
    cursor.execute(
        "SELECT stock FROM products WHERE name = ?",
        (product,)
    )
    result = cursor.fetchone()
    return result[0] if result else 0
