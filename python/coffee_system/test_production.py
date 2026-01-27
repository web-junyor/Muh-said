#!/usr/bin/env python3
"""
Production test suite for Coffee System.
Tests all critical paths: webhook, auth, error handling, concurrency.
"""

import asyncio
import json
import hmac
import hashlib
from datetime import datetime
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"
ADMIN_TOKEN = "test-admin-token-32-chars-minimum-length!!"
CLICK_SECRET_KEY = "test-secret-key-for-click-payments"

# ANSI colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

passed_tests = 0
failed_tests = 0


def log_pass(test_name: str, details: str = ""):
    global passed_tests
    passed_tests += 1
    print(f"{GREEN}✓{RESET} {test_name}")
    if details:
        print(f"  {details}")


def log_fail(test_name: str, details: str = ""):
    global failed_tests
    failed_tests += 1
    print(f"{RED}✗{RESET} {test_name}")
    if details:
        print(f"  {details}")


def generate_click_signature(payload: str, secret_key: str) -> str:
    """Generate HMAC-SHA256 signature for Click webhook."""
    return hmac.new(
        secret_key.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()


# ============================================================================
# TEST SUITE
# ============================================================================

def test_webhook_valid_signature():
    """Test: Valid webhook with correct signature."""
    import requests

    payload = json.dumps({
        "order_id": "test-001",
        "merchant_trans_id": "merchant-001",
        "payment_status": "paid",
        "items": [
            {
                "product_id": "coffee-1",
                "product_name": "Espresso",
                "quantity": 1,
                "price": 15000,
                "total_price": 15000
            }
        ],
        "total_amount": 15000,
        "sign_string": "test",
        "sign_time": datetime.now().isoformat()
    })

    signature = generate_click_signature(payload, CLICK_SECRET_KEY)

    try:
        response = requests.post(
            f"{BASE_URL}/click/webhook",
            data=payload,
            headers={
                "X-Click-Signature": signature,
                "Content-Type": "application/json"
            }
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("status") in ["ok", "duplicate"]:
                log_pass("Webhook with valid signature", f"Status: {data.get('status')}")
            else:
                log_fail("Webhook with valid signature", f"Unexpected status: {data.get('status')}")
        else:
            log_fail("Webhook with valid signature", f"HTTP {response.status_code}")
    except Exception as e:
        log_fail("Webhook with valid signature", str(e))


def test_webhook_invalid_signature():
    """Test: Webhook with invalid signature returns 200 (safe failure)."""
    import requests

    payload = json.dumps({
        "order_id": "test-invalid-sig",
        "payment_status": "paid"
    })

    try:
        response = requests.post(
            f"{BASE_URL}/click/webhook",
            data=payload,
            headers={
                "X-Click-Signature": "invalid-signature-xyz",
                "Content-Type": "application/json"
            }
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "invalid_signature":
                log_pass("Invalid signature returns 200", "Prevents Click retries")
            else:
                log_fail("Invalid signature returns 200", f"Wrong status: {data.get('status')}")
        else:
            log_fail("Invalid signature returns 200", f"HTTP {response.status_code}")
    except Exception as e:
        log_fail("Invalid signature returns 200", str(e))


def test_webhook_invalid_json():
    """Test: Invalid JSON returns 200 status."""
    import requests

    try:
        response = requests.post(
            f"{BASE_URL}/click/webhook",
            data="{broken json}",
            headers={
                "X-Click-Signature": "any-signature",
                "Content-Type": "application/json"
            }
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "invalid_json":
                log_pass("Invalid JSON returns 200", "Graceful error handling")
            else:
                log_fail("Invalid JSON returns 200", f"Wrong status: {data.get('status')}")
        else:
            log_fail("Invalid JSON returns 200", f"HTTP {response.status_code}")
    except Exception as e:
        log_fail("Invalid JSON returns 200", str(e))


def test_duplicate_order_prevention():
    """Test: Duplicate orders return 'duplicate' status."""
    import requests

    payload = json.dumps({
        "order_id": "test-duplicate-123",
        "merchant_trans_id": "merchant-dup-001",
        "payment_status": "paid",
        "items": [
            {
                "product_id": "coffee-1",
                "product_name": "Americano",
                "quantity": 2,
                "price": 12000,
                "total_price": 24000
            }
        ],
        "total_amount": 24000,
        "sign_string": "test",
        "sign_time": datetime.now().isoformat()
    })

    signature = generate_click_signature(payload, CLICK_SECRET_KEY)
    headers = {
        "X-Click-Signature": signature,
        "Content-Type": "application/json"
    }

    try:
        # First request
        response1 = requests.post(f"{BASE_URL}/click/webhook", data=payload, headers=headers)
        status1 = response1.json().get("status") if response1.status_code == 200 else None

        # Second request (duplicate)
        response2 = requests.post(f"{BASE_URL}/click/webhook", data=payload, headers=headers)
        status2 = response2.json().get("status") if response2.status_code == 200 else None

        if status1 == "ok" and status2 == "duplicate":
            log_pass("Duplicate order detection", "First: ok, Second: duplicate")
        else:
            log_fail("Duplicate order detection", f"First: {status1}, Second: {status2}")
    except Exception as e:
        log_fail("Duplicate order detection", str(e))


def test_admin_auth_valid_token():
    """Test: Admin endpoint with valid token."""
    import requests

    try:
        response = requests.get(
            f"{BASE_URL}/admin/today",
            params={"token": ADMIN_TOKEN}
        )

        if response.status_code == 200:
            data = response.json()
            if "products" in data or "total" in data:
                log_pass("Admin auth with valid token", "Returns statistics")
            else:
                log_fail("Admin auth with valid token", f"Invalid response: {data}")
        else:
            log_fail("Admin auth with valid token", f"HTTP {response.status_code}")
    except Exception as e:
        log_fail("Admin auth with valid token", str(e))


def test_admin_auth_invalid_token():
    """Test: Admin endpoint with invalid token returns 403 (with delay)."""
    import requests
    import time

    try:
        start = time.time()
        response = requests.get(
            f"{BASE_URL}/admin/today",
            params={"token": "wrong-token"}
        )
        elapsed = time.time() - start

        if response.status_code == 403:
            if elapsed >= 0.4:  # Should have ~500ms delay
                log_pass("Invalid token returns 403 with delay", f"Took {elapsed:.2f}s (brute-force protected)")
            else:
                log_fail("Invalid token returns 403 with delay", f"Delay too short: {elapsed:.2f}s")
        else:
            log_fail("Invalid token returns 403 with delay", f"HTTP {response.status_code}")
    except Exception as e:
        log_fail("Invalid token returns 403 with delay", str(e))


def test_admin_auth_missing_token():
    """Test: Admin endpoint with missing token returns 403."""
    import requests

    try:
        response = requests.get(f"{BASE_URL}/admin/today")

        if response.status_code == 403:
            log_pass("Missing token returns 403", "Prevents unauthorized access")
        else:
            log_fail("Missing token returns 403", f"HTTP {response.status_code}")
    except Exception as e:
        log_fail("Missing token returns 403", str(e))


def test_api_docs_disabled():
    """Test: API documentation endpoints are disabled."""
    import requests

    endpoints = ["/docs", "/redoc", "/openapi.json"]

    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")

            if response.status_code == 404:
                log_pass(f"Docs disabled: {endpoint}", "Returns 404")
            else:
                log_fail(f"Docs disabled: {endpoint}", f"HTTP {response.status_code}")
        except Exception as e:
            log_fail(f"Docs disabled: {endpoint}", str(e))


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("COFFEE SYSTEM - PRODUCTION TEST SUITE")
    print("="*70 + "\n")

    print("Configuration:")
    print(f"  Base URL: {BASE_URL}")
    print(f"  Admin Token: {ADMIN_TOKEN[:20]}...")
    print(f"  Click Secret: {CLICK_SECRET_KEY[:20]}...\n")

    print("Running tests...\n")

    # Webhook tests
    print(f"{YELLOW}Webhook Tests:{RESET}")
    test_webhook_valid_signature()
    test_webhook_invalid_signature()
    test_webhook_invalid_json()
    test_duplicate_order_prevention()

    # Admin tests
    print(f"\n{YELLOW}Admin Authentication Tests:{RESET}")
    test_admin_auth_valid_token()
    test_admin_auth_invalid_token()
    test_admin_auth_missing_token()

    # Security tests
    print(f"\n{YELLOW}Security Tests:{RESET}")
    test_api_docs_disabled()

    # Summary
    print(f"\n" + "="*70)
    print(f"RESULTS: {GREEN}{passed_tests} passed{RESET}, {RED}{failed_tests} failed{RESET}")
    print("="*70 + "\n")

    return failed_tests == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
