import json
import logging
from pathlib import Path
from datetime import datetime
from threading import Lock

logger = logging.getLogger(__name__)

FILE = Path("data/orders.json")
_lock = Lock()


def _ensure_data_dir() -> None:
    """Safely create data directory if missing."""
    try:
        FILE.parent.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError) as e:
        logger.error(f"Cannot create data directory: {e}")
        raise RuntimeError(f"Data directory creation failed: {e}") from e


def _load_orders() -> list:
    """
    Safely load orders from JSON file.

    Returns empty list if:
    - File doesn't exist
    - File is empty
    - File contains invalid JSON

    Never raises exception.
    """
    try:
        if not FILE.exists():
            return []

        content = FILE.read_text(encoding="utf-8")

        if not content.strip():
            logger.warning("Orders file is empty, initializing")
            return []

        data = json.loads(content)

        if not isinstance(data, list):
            logger.warning(f"Orders file corrupted (not list), resetting")
            return []

        # Validate each entry has 'id' field
        valid_orders = []
        for entry in data:
            if isinstance(entry, dict) and "id" in entry:
                valid_orders.append(entry)

        if len(valid_orders) < len(data):
            logger.warning(f"Filtered {len(data) - len(valid_orders)} invalid order entries")

        return valid_orders

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in orders file: {e}")
        return []
    except (OSError, IOError) as e:
        logger.error(f"Cannot read orders file: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error loading orders: {e}")
        return []


def _save_orders(orders: list) -> bool:
    """
    Safely save orders to JSON file with atomic write.

    Args:
        orders: List of order dicts to save

    Returns:
        True if successful, False otherwise
    """
    try:
        # Validate input
        if not isinstance(orders, list):
            logger.error("Invalid orders type for save")
            return False

        # Write to temp file first (atomic)
        temp_file = FILE.with_suffix(".tmp")

        try:
            json_content = json.dumps(orders, indent=2, ensure_ascii=False)
            temp_file.write_text(json_content, encoding="utf-8")

            # Atomic rename (Windows-safe with replace=True)
            temp_file.replace(FILE)
            return True

        finally:
            # Clean up temp file if rename failed
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except OSError:
                    pass

    except (OSError, IOError) as e:
        logger.error(f"Cannot write orders file: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error saving orders: {e}")
        return False


def is_duplicate(order_id: str) -> bool:
    """
    Check if order was already processed.

    Args:
        order_id: Click order ID to check

    Returns:
        True if order already processed, False otherwise

    Thread-safe and never raises exception.
    """
    if not order_id or not isinstance(order_id, str):
        logger.warning(f"Invalid order_id for duplicate check: {order_id}")
        return False

    with _lock:
        try:
            _ensure_data_dir()
            orders = _load_orders()

            # Check if this order_id exists
            return any(o.get("id") == order_id for o in orders)

        except Exception as e:
            logger.error(f"Error in duplicate check: {e}")
            # On error, assume NOT duplicate (allow retry)
            # This is safer than blocking legitimate retries
            return False


def save_order(order_id: str) -> bool:
    """
    Safely store processed order to prevent reprocessing.

    Args:
        order_id: Click order ID to save

    Returns:
        True if saved successfully, False on error

    Thread-safe and never raises exception.
    """
    if not order_id or not isinstance(order_id, str):
        logger.warning(f"Invalid order_id for save: {order_id}")
        return False

    with _lock:
        try:
            _ensure_data_dir()
            orders = _load_orders()

            # Check if already exists (paranoid double-check)
            if any(o.get("id") == order_id for o in orders):
                logger.info(f"Order {order_id} already saved")
                return True

            # Add new order
            new_order = {
                "id": order_id,
                "timestamp": datetime.now().isoformat()
            }
            orders.append(new_order)

            # Save atomically
            success = _save_orders(orders)
            if success:
                logger.info(f"Order {order_id} saved")
            else:
                logger.error(f"Failed to save order {order_id}")

            return success

        except Exception as e:
            logger.error(f"Error in save_order: {e}")
            return False
