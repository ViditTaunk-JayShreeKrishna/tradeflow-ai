import logging
import httpx

from app.celery_app import celery_app
from app.config import get_settings

logger = logging.getLogger(__name__)

# India's UN Comtrade reporter code
INDIA_REPORTER_CODE = 356

# HS codes we track (chapter level)
TRACKED_HS_CHAPTERS = ["61", "84", "85", "30", "71"]


@celery_app.task(name="app.tasks.trade_stats_tasks.fetch_comtrade_stats", bind=True)
def fetch_comtrade_stats(self):
    settings = get_settings()
    logger.info("Starting UN Comtrade stats fetch task...")

    if not settings.comtrade_api_key:
        logger.warning("COMTRADE_API_KEY not set. Skipping trade stats fetch.")
        return "COMTRADE_API_KEY not configured. Skipping."

    results = []

    for chapter in TRACKED_HS_CHAPTERS:
        try:
            url = (
                f"https://comtradeplus.un.org/TradeData/Yearly/HS/TOTAL/C/A/"
                f"{INDIA_REPORTER_CODE}/ALL/{chapter}/M/0/C00/0/max:100"
            )
            headers = {"Ocp-Apim-Subscription-Key": settings.comtrade_api_key}

            with httpx.Client(timeout=20.0) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

            records = data.get("data", [])
            logger.info(f"Chapter {chapter}: fetched {len(records)} records")
            results.append(f"Chapter {chapter}: {len(records)} records")

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning(f"Rate limited on chapter {chapter}. Stopping.")
                break
            logger.error(f"HTTP error for chapter {chapter}: {e}")
            results.append(f"Chapter {chapter}: HTTP error {e.response.status_code}")

        except httpx.HTTPError as e:
            logger.error(f"Request failed for chapter {chapter}: {e}")
            results.append(f"Chapter {chapter}: request failed")

        except Exception as e:
            logger.error(f"Unexpected error for chapter {chapter}: {e}")
            results.append(f"Chapter {chapter}: error — {str(e)}")

    summary = f"Trade stats fetch complete. {' | '.join(results)}"
    logger.info(summary)
    return summary