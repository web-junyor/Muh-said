import hashlib
import hmac
import os
import logging

logger = logging.getLogger(__name__)

CLICK_SECRET_KEY = os.getenv("CLICK_SECRET_KEY", "")


def verify_click_signature(raw_body: bytes, received_sign: str) -> bool:
    """
    Verify Click webhook signature using HMAC-SHA256.

    Security:
    - Constant-time comparison prevents timing attacks
    - Input validation prevents crashes
    - Never raises exception

    Args:
        raw_body: Raw request body (bytes)
        received_sign: Signature from X-Click-Signature header (str)

    Returns:
        True if valid, False otherwise

    Raises:
        RuntimeError: If CLICK_SECRET_KEY not configured
    """
    # Validate inputs
    if not isinstance(raw_body, bytes):
        logger.error(f"Invalid body type: {type(raw_body)}")
        return False

    if not isinstance(received_sign, str) or not received_sign.strip():
        logger.warning("Empty or invalid signature")
        return False

    # Check secret key
    if not CLICK_SECRET_KEY or not CLICK_SECRET_KEY.strip():
        logger.error("CLICK_SECRET_KEY not configured")
        raise RuntimeError("CLICK_SECRET_KEY not set")

    try:
        secret_bytes = CLICK_SECRET_KEY.encode("utf-8")
        computed = hashlib.sha256(raw_body + secret_bytes).hexdigest()
        # Constant-time comparison prevents timing attacks
        return hmac.compare_digest(computed, received_sign.strip())
    except Exception as e:
        logger.error(f"Signature verification error: {e}")
        return False
