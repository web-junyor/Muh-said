#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Loveble API Integration Module
Loveble webhooks va API bilan ishlash
"""

import requests
import json
import logging
import hmac
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime
from config import (
    LOVEBLE_API_KEY,
    LOVEBLE_API_URL,
    LOVEBLE_WEBHOOK_SECRET,
    LOVEBLE_SHOP_ID,
    MAX_RETRIES,
    RETRY_DELAY
)
from backend.models import LovebleWebhookPayload, LovebleOrderItem, Sale
from backend.database import db
import time

logger = logging.getLogger(__name__)


class LovebleAPIClient:
    """Loveble API bilan ishlash"""

    def __init__(self, api_key: str = LOVEBLE_API_KEY, api_url: str = LOVEBLE_API_URL):
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Loveble webhookni tekshirish"""
        try:
            expected_signature = hmac.new(
                LOVEBLE_WEBHOOK_SECRET.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False

    def get_orders(self, limit: int = 50, offset: int = 0) -> Optional[Dict[str, Any]]:
        """Loveble dan buyurtmalarni olish"""
        try:
            url = f"{self.api_url}/shops/{LOVEBLE_SHOP_ID}/orders"
            params = {
                "limit": limit,
                "offset": offset
            }

            response = self._make_request("GET", url, params=params, retries=MAX_RETRIES)
            if response and response.status_code == 200:
                return response.json()
            return None

        except Exception as e:
            logger.error(f"Error getting orders from Loveble: {e}")
            return None

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Alohida buyurtmani olish"""
        try:
            url = f"{self.api_url}/shops/{LOVEBLE_SHOP_ID}/orders/{order_id}"
            response = self._make_request("GET", url, retries=MAX_RETRIES)
            if response and response.status_code == 200:
                return response.json()
            return None

        except Exception as e:
            logger.error(f"Error getting order from Loveble: {e}")
            return None

    def get_products(self) -> Optional[Dict[str, Any]]:
        """Loveble dan mahsulotlarni olish"""
        try:
            url = f"{self.api_url}/shops/{LOVEBLE_SHOP_ID}/products"
            response = self._make_request("GET", url, retries=MAX_RETRIES)
            if response and response.status_code == 200:
                return response.json()
            return None

        except Exception as e:
            logger.error(f"Error getting products from Loveble: {e}")
            return None

    def get_stock(self, product_id: str) -> Optional[int]:
        """Mahsulotning qoldig'ini olish"""
        try:
            url = f"{self.api_url}/shops/{LOVEBLE_SHOP_ID}/products/{product_id}/stock"
            response = self._make_request("GET", url, retries=MAX_RETRIES)
            if response and response.status_code == 200:
                data = response.json()
                return data.get("stock", 0)
            return None

        except Exception as e:
            logger.error(f"Error getting stock from Loveble: {e}")
            return None

    def update_stock(self, product_id: str, quantity: int) -> bool:
        """Mahsulotning qoldig'ini yangilash"""
        try:
            url = f"{self.api_url}/shops/{LOVEBLE_SHOP_ID}/products/{product_id}/stock"
            payload = {"stock": quantity}
            response = self._make_request("PUT", url, json=payload, retries=MAX_RETRIES)

            if response and response.status_code in [200, 201]:
                logger.info(f"Stock updated for product {product_id}: {quantity}")
                return True
            else:
                logger.error(f"Failed to update stock for product {product_id}")
                return False

        except Exception as e:
            logger.error(f"Error updating stock: {e}")
            return False

    def process_order_event(self, webhook_payload: Dict[str, Any]) -> bool:
        """Loveble webhookdan kelgan buyurtmani qayta ishlash"""
        try:
            event_type = webhook_payload.get("event_type")
            order_id = webhook_payload.get("order_id")

            # Webhook logga yozish
            db.log_webhook(
                event_type=event_type,
                order_id=order_id,
                payload=webhook_payload,
                status="processing"
            )

            # Faqat to'langan buyurtmalarni qayta ishlash
            if event_type in ["order_paid", "order_completed"]:
                items = webhook_payload.get("items", [])

                for item in items:
                    product_name = item.get("product_name")
                    quantity = item.get("quantity")
                    price = item.get("price")
                    total_price = item.get("total_price")

                    # Sotuvni qaydda olish
                    sale = Sale(
                        id=f"{order_id}_{product_name}",
                        product_id=item.get("product_id"),
                        product_name=product_name,
                        quantity=quantity,
                        price=price,
                        total_price=total_price,
                        check_id=order_id,
                        loveble_order_id=order_id,
                        payment_method=webhook_payload.get("payment_method", "cash"),
                        status="completed",
                        timestamp=datetime.now().isoformat()
                    )

                    db.register_sale(sale)

                # Webhook statusini "processed" qilib yangilash
                db.log_webhook(
                    event_type=event_type,
                    order_id=order_id,
                    payload=webhook_payload,
                    status="processed"
                )

                logger.info(f"Order {order_id} processed successfully")
                return True

            return False

        except Exception as e:
            logger.error(f"Error processing order event: {e}")
            db.log_webhook(
                event_type=webhook_payload.get("event_type"),
                order_id=webhook_payload.get("order_id"),
                payload=webhook_payload,
                status="error",
                error_msg=str(e)
            )
            return False

    def _make_request(
        self,
        method: str,
        url: str,
        json: Optional[Dict] = None,
        params: Optional[Dict] = None,
        retries: int = 1
    ) -> Optional[requests.Response]:
        """API request qilish (retry bilan)"""

        attempt = 0
        while attempt < retries:
            try:
                if method == "GET":
                    response = requests.get(
                        url,
                        headers=self.headers,
                        params=params,
                        timeout=10
                    )
                elif method == "POST":
                    response = requests.post(
                        url,
                        headers=self.headers,
                        json=json,
                        timeout=10
                    )
                elif method == "PUT":
                    response = requests.put(
                        url,
                        headers=self.headers,
                        json=json,
                        timeout=10
                    )
                elif method == "DELETE":
                    response = requests.delete(
                        url,
                        headers=self.headers,
                        timeout=10
                    )
                else:
                    logger.error(f"Unsupported HTTP method: {method}")
                    return None

                response.raise_for_status()
                return response

            except requests.exceptions.Timeout:
                attempt += 1
                if attempt < retries:
                    logger.warning(f"Request timeout, retry {attempt}/{retries}")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Request timeout after {retries} retries")
                    return None

            except requests.exceptions.ConnectionError:
                attempt += 1
                if attempt < retries:
                    logger.warning(f"Connection error, retry {attempt}/{retries}")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Connection error after {retries} retries")
                    return None

            except requests.exceptions.HTTPError as e:
                attempt += 1
                if attempt < retries and response.status_code >= 500:
                    logger.warning(f"HTTP {response.status_code}, retry {attempt}/{retries}")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"HTTP error: {e}")
                    return None

            except Exception as e:
                logger.error(f"Request error: {e}")
                return None

        return None


# Global Loveble API client
loveble_client = LovebleAPIClient()
