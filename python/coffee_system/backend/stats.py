import json
import logging
from datetime import date
from pathlib import Path
from threading import Lock

logger = logging.getLogger(__name__)

FILE = Path("data/daily_stats.json")
FILE.parent.mkdir(exist_ok=True)
_lock = Lock()


def _load_stats() -> dict:
    """
    Safely load stats from JSON.
    Returns {} on any error (file missing, JSON corruption, etc).
    """
    if not FILE.exists():
        return {}
    try:
        content = FILE.read_text().strip()
        if not content:
            return {}
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"Stats JSON corruption: {e}")
        return {}
    except Exception as e:
        logger.error(f"Stats load error: {e}")
        return {}


def update_stats(items):
    """
    Thread-safe daily stats update.

    Args:
        items: List of OrderItem objects with product_name, quantity, total_price
    """
    with _lock:
        try:
            today = str(date.today())
            stats = _load_stats()

            if today not in stats:
                stats[today] = {"products": {}, "total": 0}

            for item in items:
                pname = item.product_name
                stats[today]["products"][pname] = stats[today]["products"].get(pname, 0) + item.quantity
                stats[today]["total"] += item.total_price

            FILE.write_text(json.dumps(stats, indent=2))
        except Exception as e:
            logger.error(f"Stats update failed: {e}")


def get_today_stats() -> dict:
    """
    Get today's sales summary.

    Returns:
        Dict with products and total, or empty dict if no data
    """
    with _lock:
        today = str(date.today())
        stats = _load_stats()
        return stats.get(today, {"products": {}, "total": 0})


def get_all_stats() -> dict:
    """
    Get all historical stats.

    Returns:
        Dict of all stats by date, or empty dict if file missing
    """
    with _lock:
        return _load_stats()
