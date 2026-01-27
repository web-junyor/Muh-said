import asyncio
import logging
from fastapi import FastAPI, HTTPException, Request
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from pytz import timezone
import hmac
import os
from pathlib import Path
from contextlib import asynccontextmanager

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    # If python-dotenv not installed, manually read .env
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()
from backend.telegram import send_message
from backend.click_webhook import click_webhook

logger = logging.getLogger(__name__)

# Global scheduler reference
scheduler = None


async def start_scheduler():
    """Initialize and run APScheduler."""
    global scheduler
    scheduler = AsyncIOScheduler(timezone=TZ)

    # Schedule daily report at 23:00
    scheduler.add_job(
        send_daily_report,
        "cron",
        hour=23,
        minute=0,
        name="daily_report"
    )

    scheduler.start()
    logger.info("Scheduler started - daily report at 23:00")


async def shutdown_scheduler():
    """Properly shutdown scheduler."""
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("Scheduler shut down")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifespan - startup and shutdown."""
    await start_scheduler()
    yield
    await shutdown_scheduler()


# Disable API docs for security (no info leak)
app = FastAPI(
    title="Coffee System API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan
)

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
TZ = timezone("Asia/Tashkent")

# Startup validation
if not ADMIN_TOKEN or not ADMIN_TOKEN.strip():
    logger.warning("ADMIN_TOKEN not set - admin endpoint will be inaccessible")
elif len(ADMIN_TOKEN) < 16:
    logger.warning("ADMIN_TOKEN is too short (< 16 chars), recommend 32+")


def admin_auth(token: str) -> bool:
    """
    Verify admin token using constant-time comparison.
    Prevents timing attacks.

    Args:
        token: Token to verify

    Returns:
        True if valid, False otherwise
    """
    if not token or not isinstance(token, str):
        return False
    # Constant-time comparison
    return hmac.compare_digest(token.strip(), ADMIN_TOKEN or "")


@app.get("/admin/today")
async def admin_today(token: str = ""):
    """
    Get today's statistics (admin only).

    Security:
    - Token-based access control
    - Constant-time token comparison
    - Brute-force protection (500ms delay on failed auth)

    Args:
        token: Admin authentication token

    Returns:
        JSON with daily statistics
    """
    if not ADMIN_TOKEN:
        raise HTTPException(status_code=500, detail="API not configured")

    if not admin_auth(token):
        # Brute-force protection: delay failed attempts
        await asyncio.sleep(0.5)
        logger.warning("Unauthorized admin access attempt")
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        return get_today_stats()
    except Exception as e:
        logger.error(f"Stats fetch error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


@app.post("/click/webhook")
async def webhook(request: Request):
    """
    Click payment webhook endpoint.

    Security:
    - HMAC-SHA256 signature verification required
    - Always returns 200 for safety (prevents Click retries on errors)
    - Rate limiting via async queue
    - Comprehensive error handling

    Args:
        request: FastAPI request

    Returns:
        JSON status (always 200 even on errors)
    """
    try:
        result = await click_webhook(request)
        return result
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=False)
        # Return 200 to stop Click from retrying
        return {"status": "error"}


async def send_daily_report():
    """Send daily sales report at 23:00."""
    try:
        stats = get_today_stats()
        if not stats or not stats.get("products"):
            message = "📊 No sales today"
        else:
            products = stats.get("products", {})
            total = stats.get("total", 0)

            items_text = "\n".join(
                [f"• {name}: {qty} ta" for name, qty in products.items()]
            )

            message = (
                f"📊 *KUNLIK HISOBOT*\n\n"
                f"{items_text}\n\n"
                f"💰 Jami: {total:,} UZS"
            )

        await send_message(message)
        logger.info("Daily report sent successfully")
    except Exception as e:
        logger.error(f"Daily report error: {e}")


if __name__ == "__main__":
    import uvicorn

    logging.basicConfig(level=logging.INFO)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        loop="asyncio"
    )
