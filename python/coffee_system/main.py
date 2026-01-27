#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coffee System - FastAPI + Telegram Bot Entry Point
Starts the server and bot together
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path so we can import backend
sys.path.insert(0, str(Path(__file__).parent))

from backend.main import app

if __name__ == "__main__":
    import uvicorn

    logging.basicConfig(level=logging.INFO)

    print("\n" + "="*60)
    print("[*] Coffee System Starting")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=3000,
        loop="asyncio"
    )
