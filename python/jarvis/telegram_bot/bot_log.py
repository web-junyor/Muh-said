# -*- coding: utf-8 -*-
"""Bot log — oxirgi N ta hodisa (xotira)."""
from collections import deque
from datetime import datetime
from typing import List, Tuple

LOG_MAX = 100
_log: deque = deque(maxlen=LOG_MAX)


def log_event(message: str) -> None:
    """Yangi hodisani qo'shadi."""
    ts = datetime.utcnow().strftime("%H:%M:%S")
    _log.append((ts, message))


def get_recent(n: int = 30) -> List[Tuple[str, str]]:
    """Oxirgi n ta (vaqt, xabar) ro'yxati."""
    return list(_log)[-n:][::-1]
