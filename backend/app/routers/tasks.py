from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from app.celery_app import celery_app
from app.tasks.forex_tasks import update_forex_rates
from app.tasks.trade_stats_tasks import fetch_comtrade_stats

router = APIRouter(prefix="/tasks", tags=["Data Pipeline"])


def _task_info(task_id: str) -> dict:
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": str(result.result) if result.ready() else None,
        "successful": result.successful() if result.ready() else None,
    }


@router.post("/trigger/forex")
async def trigger_forex_update():
    task = update_forex_rates.delay()
    return {
        "message": "Forex rate update task queued",
        "task_id": task.id,
        "status": "PENDING",
    }


@router.post("/trigger/trade-stats")
async def trigger_trade_stats():
    task = fetch_comtrade_stats.delay()
    return {
        "message": "Trade statistics fetch task queued",
        "task_id": task.id,
        "status": "PENDING",
    }


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    try:
        return _task_info(task_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid task ID: {str(e)}")


@router.get("/active")
async def get_active_tasks():
    inspector = celery_app.control.inspect()
    active = inspector.active() or {}
    scheduled = inspector.scheduled() or {}
    return {
        "active_tasks": active,
        "scheduled_tasks": scheduled,
    }