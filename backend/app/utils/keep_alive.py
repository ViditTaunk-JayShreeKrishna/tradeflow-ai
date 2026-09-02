"""
Keep-alive script for Render.com free tier.
Render free services sleep after 15 minutes of inactivity.
This script pings the health endpoint every 14 minutes to prevent sleeping.

Run this as a separate Render cron job or background worker.
"""

import time
import httpx
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = os.getenv("BACKEND_URL", "https://your-app.onrender.com")
PING_INTERVAL = 14 * 60  # 14 minutes


def ping():
    try:
        response = httpx.get(f"{BACKEND_URL}/health", timeout=10.0)
        logger.info(f"Ping successful: {response.status_code} — {response.json()}")
    except Exception as e:
        logger.warning(f"Ping failed: {e}")


if __name__ == "__main__":
    logger.info(f"Keep-alive started. Pinging {BACKEND_URL} every 14 minutes.")
    while True:
        ping()
        time.sleep(PING_INTERVAL)