"""Prometheus metrics."""

from prometheus_client import Counter, Gauge

POSTS_PUBLISHED = Counter("telegram_posts_published_total", "Number of Telegram posts published")
MODERATION_ACTIONS = Counter("moderation_actions_total", "Moderation actions", ["action"])
QUEUE_DEPTH = Gauge("content_queue_depth", "Scheduled content items awaiting publication")
