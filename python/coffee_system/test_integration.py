#!/usr/bin/env python3
"""
Integration test for SAID Coffee System.

Tests:
1. Module imports
2. Environment variable setup
3. Data directory creation
4. JSON file initialization
5. Signature verification
6. Statistics collection
7. PDF generation
8. Telegram connectivity (mock)
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, date

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    print("[TEST] Module imports...")
    try:
        from backend import models, security, storage, stats, pdf, telegram, click_webhook, main
        print("  ✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_environment():
    """Test environment variables."""
    print("[TEST] Environment variables...")
    required = ["BOT_TOKEN", "CHAT_ID", "CLICK_SECRET_KEY", "ADMIN_TOKEN"]
    missing = []

    for var in required:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print(f"  ⚠ Missing: {', '.join(missing)}")
        print(f"    → Set these in .env file")
        return False
    else:
        print("  ✓ All environment variables set")
        return True

def test_data_directories():
    """Test data directory creation."""
    print("[TEST] Data directories...")
    try:
        Path("data").mkdir(exist_ok=True)
        Path("data/receipts").mkdir(parents=True, exist_ok=True)
        print("  ✓ Data directories created")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def test_json_files():
    """Test JSON file initialization."""
    print("[TEST] JSON file initialization...")
    try:
        # Initialize orders.json
        orders_file = Path("data/orders.json")
        if not orders_file.exists():
            orders_file.write_text("[]", encoding="utf-8")

        # Initialize daily_stats.json
        stats_file = Path("data/daily_stats.json")
        if not stats_file.exists():
            stats_file.write_text("{}", encoding="utf-8")

        # Verify files are valid JSON
        json.loads(orders_file.read_text())
        json.loads(stats_file.read_text())

        print("  ✓ JSON files initialized and valid")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def test_signature_verification():
    """Test Click signature verification."""
    print("[TEST] Signature verification...")
    try:
        from backend.security import verify_click_signature
        import hashlib
        import hmac

        secret = os.getenv("CLICK_SECRET_KEY", "test_secret")
        body = b"test_payload"

        # Compute correct signature
        correct_sig = hashlib.sha256(body + secret.encode()).hexdigest()

        # Test valid signature
        if verify_click_signature(body, correct_sig):
            print("  ✓ Valid signature accepted")
        else:
            print("  ✗ Valid signature rejected")
            return False

        # Test invalid signature
        try:
            verify_click_signature(body, "invalid_signature")
            print("  ✗ Invalid signature accepted (should reject)")
            return False
        except Exception:
            print("  ✓ Invalid signature rejected")

        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def test_storage():
    """Test storage layer."""
    print("[TEST] Storage/Idempotency...")
    try:
        from backend.storage import is_duplicate, save_order

        test_order_id = f"test_order_{datetime.now().timestamp()}"

        # Should not be duplicate initially
        if is_duplicate(test_order_id):
            print("  ✗ New order marked as duplicate")
            return False

        # Save order
        save_order(test_order_id)

        # Should be duplicate now
        if not is_duplicate(test_order_id):
            print("  ✗ Saved order not detected as duplicate")
            return False

        print("  ✓ Storage and idempotency working")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def test_statistics():
    """Test statistics collection."""
    print("[TEST] Statistics collection...")
    try:
        from backend.stats import update_stats, get_today_stats
        from backend.models import ItemModel

        test_items = [
            ItemModel(
                product_id="p1",
                product_name="Test Espresso",
                quantity=2,
                price=12000,
                total_price=24000
            )
        ]

        # Update stats
        update_stats(test_items)

        # Get stats
        today_stats = get_today_stats()

        if today_stats and "products" in today_stats:
            if "Test Espresso" in today_stats["products"]:
                print("  ✓ Statistics collection working")
                return True

        print("  ✗ Statistics not collected properly")
        return False
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def test_pdf_generation():
    """Test PDF generation."""
    print("[TEST] PDF generation...")
    try:
        from backend.pdf import generate_pdf
        from backend.models import ItemModel

        test_items = [
            ItemModel(
                product_id="p1",
                product_name="Test Mocha",
                quantity=1,
                price=15000,
                total_price=15000
            )
        ]

        pdf_path = generate_pdf("test_order_12345", test_items, 15000)

        if pdf_path.exists() and pdf_path.stat().st_size > 0:
            print(f"  ✓ PDF generated: {pdf_path}")
            return True
        else:
            print("  ✗ PDF file not created or empty")
            return False
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def test_telegram_initialization():
    """Test Telegram bot initialization."""
    print("[TEST] Telegram initialization...")
    try:
        from backend.telegram import bot, CHAT_ID

        if not os.getenv("BOT_TOKEN"):
            print("  ⚠ BOT_TOKEN not set (skipping actual send test)")
            return True

        if bot:
            print("  ✓ Bot initialized")
            return True
        else:
            print("  ✗ Bot not initialized")
            return False
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def test_models():
    """Test Pydantic models."""
    print("[TEST] Pydantic models...")
    try:
        from backend.models import ItemModel, OrderPaid

        # Valid item
        item = ItemModel(
            product_id="p1",
            product_name="Espresso",
            quantity=1,
            price=12000,
            total_price=12000
        )

        # Valid order
        order = OrderPaid(
            order_id="order_123",
            merchant_trans_id="mec_456",
            payment_status="paid",
            items=[item],
            total_amount=12000,
            sign_string="abc123",
            sign_time="2026-01-27 14:30:00"
        )

        print("  ✓ Pydantic models valid")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*50)
    print("SAID COFFEE SYSTEM - INTEGRATION TEST")
    print("="*50 + "\n")

    results = []

    results.append(("Module Imports", test_imports()))
    results.append(("Environment", test_environment()))
    results.append(("Data Directories", test_data_directories()))
    results.append(("JSON Files", test_json_files()))
    results.append(("Signature Verification", test_signature_verification()))
    results.append(("Storage/Idempotency", test_storage()))
    results.append(("Statistics", test_statistics()))
    results.append(("PDF Generation", test_pdf_generation()))
    results.append(("Telegram Init", test_telegram_initialization()))
    results.append(("Models", test_models()))

    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {test_name:.<40} {status}")

    print(f"\nTotal: {passed}/{total} passed")

    if passed == total:
        print("\n✓ All tests passed! System is ready for deployment.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Review above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
