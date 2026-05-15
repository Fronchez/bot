"""Background jobs for autonomous operation."""

import asyncio

import structlog

from app.db.session import AsyncSessionFactory
from app.observability.metrics import POSTS_PUBLISHED
from app.repositories.content import ContentRepository
from app.services.decision_engine import DecisionEngine
from app.services.telegram_publisher import TelegramPublisher
from app.workers.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="app.workers.tasks.run_decision_cycle")
def run_decision_cycle() -> dict[str, float | str]:
    """Celery wrapper for the autonomous strategy loop."""
    return asyncio.run(_run_decision_cycle())


async def _run_decision_cycle() -> dict[str, float | str]:
    async with AsyncSessionFactory() as session:
        result = await DecisionEngine(session).run_cycle()
        logger.info("decision_cycle_completed", **result)
        return result


@celery_app.task(name="app.workers.tasks.publish_due_content")
def publish_due_content() -> int:
    """Celery wrapper for scheduled publication."""
    return asyncio.run(_publish_due_content())


async def _publish_due_content() -> int:
    published = 0
    publisher = TelegramPublisher()
    async with AsyncSessionFactory() as session:
        items = await ContentRepository(session).due_for_publication(limit=3)
        for item in items:
            await publisher.publish(session, item)
            POSTS_PUBLISHED.inc()
            published += 1
    logger.info("published_due_content", count=published)
    return published
