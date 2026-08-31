import logging
from datetime import date
from sqlalchemy.exc import IntegrityError
import httpx

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.exchange_rate import ExchangeRate
from app.config import get_settings

logger = logging.getLogger(__name__)

SUPPORTED_CURRENCIES = [
    "INR", "CNY", "EUR", "GBP", "AED",
    "JPY", "SGD", "AUD", "BRL", "ZAR",
    "CAD", "KRW", "THB"
]


@celery_app.task(name="app.tasks.forex_tasks.update_forex_rates", bind=True)
def update_forex_rates(self):
    settings = get_settings()
    logger.info("Starting forex rate update task...")

    if not settings.exchangerate_api_key:
        logger.warning("EXCHANGERATE_API_KEY not set. Using fallback rates.")
        return _use_fallback_rates()

    try:
        url = f"https://v6.exchangerate-api.com/v6/{settings.exchangerate_api_key}/latest/USD"
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()

        if data.get("result") != "success":
            raise ValueError(f"API returned non-success: {data.get('error-type')}")

        rates = data["conversion_rates"]
        today = date.today()
        db = SessionLocal()
        updated = 0
        skipped = 0

        try:
            for currency in SUPPORTED_CURRENCIES:
                if currency not in rates:
                    continue
                try:
                    rate_obj = ExchangeRate(
                        base_currency="USD",
                        target_currency=currency,
                        rate=rates[currency],
                        date=today,
                        source="exchangerate-api",
                    )
                    db.add(rate_obj)
                    db.flush()
                    updated += 1
                except IntegrityError:
                    db.rollback()
                    # Rate for today already exists — update it
                    existing = db.query(ExchangeRate).filter(
                        ExchangeRate.base_currency == "USD",
                        ExchangeRate.target_currency == currency,
                        ExchangeRate.date == today,
                    ).first()
                    if existing:
                        existing.rate = rates[currency]
                        existing.source = "exchangerate-api"
                        updated += 1
                    else:
                        skipped += 1

            db.commit()
            result = f"Forex update complete. Updated: {updated}, Skipped: {skipped}"
            logger.info(result)
            return result

        finally:
            db.close()

    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching forex rates: {e}")
        raise self.retry(exc=e, countdown=300, max_retries=3)
    except Exception as e:
        logger.error(f"Forex task failed: {e}")
        raise


def _use_fallback_rates():
    """Use hardcoded fallback rates when API key is missing."""
    fallback = {
        "INR": 83.5, "CNY": 7.24, "EUR": 0.92, "GBP": 0.79,
        "AED": 3.67, "JPY": 149.2, "SGD": 1.34, "AUD": 1.53,
        "BRL": 4.97, "ZAR": 18.63, "CAD": 1.36, "KRW": 1325.0, "THB": 35.1
    }
    today = date.today()
    db = SessionLocal()
    updated = 0

    try:
        for currency, rate in fallback.items():
            try:
                rate_obj = ExchangeRate(
                    base_currency="USD",
                    target_currency=currency,
                    rate=rate,
                    date=today,
                    source="fallback_seed",
                )
                db.add(rate_obj)
                db.flush()
                updated += 1
            except IntegrityError:
                db.rollback()

        db.commit()
        return f"Fallback rates applied. Updated: {updated}"
    finally:
        db.close()