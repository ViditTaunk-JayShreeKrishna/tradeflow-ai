from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "tradeflow",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.forex_tasks",
        "app.tasks.trade_stats_tasks",
    ]
)

celery_app.conf.timezone = "UTC"
celery_app.conf.task_track_started = True
celery_app.conf.result_expires = 3600  # results expire after 1 hour

celery_app.conf.beat_schedule = {
    "update-forex-rates-every-hour": {
        "task": "app.tasks.forex_tasks.update_forex_rates",
        "schedule": crontab(minute=0),          # top of every hour
    },
    "fetch-comtrade-stats-weekly": {
        "task": "app.tasks.trade_stats_tasks.fetch_comtrade_stats",
        "schedule": crontab(hour=2, minute=0, day_of_week=1),  # Monday 2am UTC
    },
}