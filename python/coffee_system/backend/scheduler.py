#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduler for Daily, Weekly, and Monthly Diagnostics
23:00 da kunlik, juma kuni haftalik, oyning 1-quni oylik diagnostika
"""

import logging
import asyncio
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List, Callable
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import json

from config import (
    DAILY_DIAGNOSTIC_HOUR,
    DAILY_DIAGNOSTIC_MINUTE,
    WEEKLY_DIAGNOSTIC_DAY,
    MONTHLY_DIAGNOSTIC_DAY,
    TIMEZONE,
    LOW_STOCK_THRESHOLD,
    MESSAGES
)

logger = logging.getLogger(__name__)


class DiagnosticsScheduler:
    """Diagnostika jadvalini boshqarish"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=TIMEZONE)
        self.callbacks = []

    def add_diagnostic_callback(self, callback: Callable):
        """Diagnostika javobi uchun callback qo'shish"""
        self.callbacks.append(callback)

    async def notify_callbacks(self, report_type: str, report_data: Dict):
        """Barcha callbacklarga xabar berish"""
        for callback in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(report_type, report_data)
                else:
                    callback(report_type, report_data)
            except Exception as e:
                logger.error(f"Error in diagnostic callback: {e}")

    async def run_daily_diagnostic(self):
        """Kunlik diagnostika (23:00)"""
        try:
            logger.info("Running daily diagnostic...")

            from backend.database import db
            from backend.models import DailyReport

            today = date.today()
            products = db.get_all_products()
            sales = db.get_sales_by_date(today)
            stock_levels = db.get_all_stock_levels()
            low_stock_products = db.get_low_stock_products(LOW_STOCK_THRESHOLD)

            # Hisobotni tuzish
            total_sales = len(sales)
            total_revenue = sum(sale.total_price for sale in sales)
            products_sold = {}

            for sale in sales:
                if sale.product_name not in products_sold:
                    products_sold[sale.product_name] = 0
                products_sold[sale.product_name] += sale.quantity

            report = DailyReport(
                date=today.isoformat(),
                total_sales=total_sales,
                total_revenue=total_revenue,
                products_sold=products_sold,
                stock_levels=stock_levels,
                low_stock_products=low_stock_products,
                report_time=datetime.now().isoformat()
            )

            # Hisobotni saqlash
            db.save_daily_report(report)

            # Callbackga xabar berish
            await self.notify_callbacks("daily", report.to_dict())

            logger.info(f"Daily diagnostic completed: {total_sales} sales, {total_revenue} som")

        except Exception as e:
            logger.error(f"Error in daily diagnostic: {e}")

    async def run_weekly_diagnostic(self):
        """Haftalik diagnostika (Juma 23:05)"""
        try:
            logger.info("Running weekly diagnostic...")

            from backend.database import db
            from backend.models import WeeklyReport

            today = date.today()
            start_date = today - timedelta(days=today.weekday())  # Dushanba
            end_date = start_date + timedelta(days=6)  # Yakshanba

            # Bu haftaning sotuvlarini olish
            all_sales = []
            for i in range(7):
                day = start_date + timedelta(days=i)
                all_sales.extend(db.get_sales_by_date(day))

            week_number = today.isocalendar()[1]
            year = today.year

            # Hisobotni tuzish
            total_sales = len(all_sales)
            total_revenue = sum(sale.total_price for sale in all_sales)
            products_sold = {}

            for sale in all_sales:
                if sale.product_name not in products_sold:
                    products_sold[sale.product_name] = 0
                products_sold[sale.product_name] += sale.quantity

            # Eng ko'p va eng kam sotilgan mahsulotlar
            best_selling = max(products_sold, key=products_sold.get) if products_sold else "N/A"
            worst_selling = min(products_sold, key=products_sold.get) if products_sold else "N/A"

            # O'rtacha kunlik sotuvlar
            average_daily_sales = total_sales / 7 if total_sales > 0 else 0

            # Inventar samaradorligi (davlat-da qolgan/dastlabki miqdor)
            stock_levels = db.get_all_stock_levels()
            total_remaining = sum(stock_levels.values())
            total_initial = 12 * len(stock_levels)  # 8 ta mahsulot x 12 dona
            stock_efficiency = (1 - (total_remaining / total_initial)) * 100 if total_initial > 0 else 0

            report = WeeklyReport(
                week_number=week_number,
                year=year,
                total_sales=total_sales,
                total_revenue=total_revenue,
                products_sold=products_sold,
                average_daily_sales=average_daily_sales,
                best_selling_product=best_selling,
                worst_selling_product=worst_selling,
                stock_efficiency=round(stock_efficiency, 2),
                report_time=datetime.now().isoformat()
            )

            # Hisobotni saqlash
            db.save_weekly_report(report)

            # Callbackga xabar berish
            await self.notify_callbacks("weekly", report.to_dict())

            logger.info(f"Weekly diagnostic completed: {total_sales} sales, {total_revenue} som")

        except Exception as e:
            logger.error(f"Error in weekly diagnostic: {e}")

    async def run_monthly_diagnostic(self):
        """Oylik diagnostika (Oyning 1-quni 23:10)"""
        try:
            logger.info("Running monthly diagnostic...")

            from backend.database import db
            from backend.models import MonthlyReport

            today = date.today()
            month = today.month
            year = today.year

            # O'tgan oyning sotuv ma'lumotlarini olish
            if month == 1:
                prev_month = 12
                prev_year = year - 1
            else:
                prev_month = month - 1
                prev_year = year

            start_date = date(prev_year, prev_month, 1)
            if prev_month == 12:
                end_date = date(prev_year, prev_month, 31)
            else:
                end_date = date(prev_year, prev_month + 1, 1) - timedelta(days=1)

            # Oylik sotuvlarni olish
            products = db.get_all_products()
            all_sales = []
            for product in products:
                all_sales.extend(
                    db.get_sales_by_product(
                        product.name,
                        start_date=start_date,
                        end_date=end_date
                    )
                )

            # Hisobotni tuzish
            total_sales = len(all_sales)
            total_revenue = sum(sale.total_price for sale in all_sales)
            products_sold = {}

            for sale in all_sales:
                if sale.product_name not in products_sold:
                    products_sold[sale.product_name] = 0
                products_sold[sale.product_name] += sale.quantity

            # Eng ko'p va eng kam sotilgan mahsulotlar
            best_selling = max(products_sold, key=products_sold.get) if products_sold else "N/A"
            worst_selling = min(products_sold, key=products_sold.get) if products_sold else "N/A"

            # Eng ko'p daromad olinadigan mahsulot
            product_revenue = {}
            for sale in all_sales:
                if sale.product_name not in product_revenue:
                    product_revenue[sale.product_name] = 0
                product_revenue[sale.product_name] += sale.total_price

            most_profitable = max(product_revenue, key=product_revenue.get) if product_revenue else "N/A"

            # O'rtacha kunlik so'zlamalar
            days_in_month = (end_date - start_date).days + 1
            average_daily_sales = total_sales / days_in_month if days_in_month > 0 else 0
            average_daily_revenue = total_revenue // days_in_month if days_in_month > 0 else 0

            # Inventar samaradorligi
            stock_levels = db.get_all_stock_levels()
            total_remaining = sum(stock_levels.values())
            total_initial = 12 * len(stock_levels)
            stock_efficiency = (1 - (total_remaining / total_initial)) * 100 if total_initial > 0 else 0

            # O'sish foizi (o'tgan oyga nisbatan)
            growth_percentage = 0.0

            report = MonthlyReport(
                month=prev_month,
                year=prev_year,
                total_sales=total_sales,
                total_revenue=total_revenue,
                products_sold=products_sold,
                average_daily_sales=round(average_daily_sales, 2),
                average_daily_revenue=average_daily_revenue,
                best_selling_product=best_selling,
                worst_selling_product=worst_selling,
                most_profitable_product=most_profitable,
                stock_efficiency=round(stock_efficiency, 2),
                growth_percentage=round(growth_percentage, 2),
                report_time=datetime.now().isoformat()
            )

            # Hisobotni saqlash
            db.save_monthly_report(report)

            # Callbackga xabar berish
            await self.notify_callbacks("monthly", report.to_dict())

            logger.info(f"Monthly diagnostic completed: {total_sales} sales, {total_revenue} som")

        except Exception as e:
            logger.error(f"Error in monthly diagnostic: {e}")

    def start(self):
        """Schedulerni ishga tushirish"""
        try:
            # Kunlik diagnostika - har kuni 23:00
            self.scheduler.add_job(
                self.run_daily_diagnostic,
                CronTrigger(
                    hour=DAILY_DIAGNOSTIC_HOUR,
                    minute=DAILY_DIAGNOSTIC_MINUTE,
                    timezone=TIMEZONE
                ),
                id="daily_diagnostic",
                name="Daily Diagnostic",
                replace_existing=True
            )

            # Haftalik diagnostika - Juma 23:05
            self.scheduler.add_job(
                self.run_weekly_diagnostic,
                CronTrigger(
                    day_of_week="fri",
                    hour=23,
                    minute=5,
                    timezone=TIMEZONE
                ),
                id="weekly_diagnostic",
                name="Weekly Diagnostic",
                replace_existing=True
            )

            # Oylik diagnostika - Oyning 1-quni 23:10
            self.scheduler.add_job(
                self.run_monthly_diagnostic,
                CronTrigger(
                    day=MONTHLY_DIAGNOSTIC_DAY,
                    hour=23,
                    minute=10,
                    timezone=TIMEZONE
                ),
                id="monthly_diagnostic",
                name="Monthly Diagnostic",
                replace_existing=True
            )

            self.scheduler.start()
            logger.info("Diagnostics scheduler started successfully")

        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
            raise

    def shutdown(self):
        """Schedulerni to'xtatish"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("Diagnostics scheduler shut down")
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {e}")


# Global scheduler instance
diagnostics_scheduler = DiagnosticsScheduler()
