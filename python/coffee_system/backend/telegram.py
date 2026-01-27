import os
import logging
from aiogram import Bot
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")

bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None

# Rate limiting: Telegram API limit is 30 msg/sec, we use 5 concurrent
_message_semaphore = asyncio.Semaphore(5)


async def send_message(text: str) -> bool:
    """
    Send text message to admin chat with rate limiting.
    Supports HTML formatting (<b>, <i>, <code>, etc).

    Security:
    - Text length validation (max 4096 chars)
    - Rate limiting prevents Telegram API throttling
    - Never raises exception (always returns bool)

    Args:
        text: Message text (can include HTML tags)

    Returns:
        True if sent, False otherwise
    """
    if not bot:
        return False

    if not isinstance(text, str) or not text.strip():
        return False

    if len(text) > 4096:
        logger.warning(f"Message too long ({len(text)}), truncating")
        text = text[:4093] + "..."

    async with _message_semaphore:
        try:
            await bot.send_message(chat_id=int(CHAT_ID), text=text, parse_mode="HTML")
            return True
        except Exception as e:
            logger.error(f"Message send failed: {e}", exc_info=False)
            return False


async def send_document(file_path) -> bool:
    """
    Send PDF receipt to admin chat.

    Security:
    - Path traversal prevention (whitelist data/receipts)
    - File size validation (max 20MB)
    - File existence check
    - Never raises exception

    Args:
        file_path: Path to PDF file

    Returns:
        True if sent, False otherwise
    """
    if not bot:
        return False

    try:
        path = Path(file_path)

        # Security: prevent path traversal attacks
        try:
            path.resolve().relative_to(Path("data/receipts").resolve())
        except ValueError:
            logger.error(f"Path traversal attempt: {file_path}")
            return False

        if not path.exists():
            logger.warning(f"PDF not found: {file_path}")
            return False

        # File size limit (20MB)
        file_size = path.stat().st_size
        if file_size > 20 * 1024 * 1024:
            logger.error(f"File too large: {file_size} bytes")
            return False

        async with _message_semaphore:
            with open(path, "rb") as f:
                await bot.send_document(chat_id=int(CHAT_ID), document=f)
            return True

    except Exception as e:
        logger.error(f"Document send failed: {e}", exc_info=False)
        return False
