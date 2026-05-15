"""Celery application and schedule."""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()
celery_app = Celery("autonomous_bot", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.timezone = settings.posting_timezone
celery_app.conf.beat_schedule = {
    "decision-cycle-every-30-minutes": {
        "task": "app.workers.tasks.run_decision_cycle",
        "schedule": 1800.0,
    },
    "publish-due-content-every-minute": {
        "task": "app.workers.tasks.publish_due_content",
        "schedule": 60.0,
    },
}
celery_app.conf.task_routes = {
    "app.workers.tasks.run_decision_cycle": {"queue": "strategy"},
    "app.workers.tasks.publish_due_content": {"queue": "publishing"},
}
