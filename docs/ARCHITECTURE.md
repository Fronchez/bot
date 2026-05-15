# Architecture and workflows

## Bounded contexts

| Context | Responsibility | Key files |
| --- | --- | --- |
| API/Admin | Admin dashboard API, rate limits, auth | `app/main.py`, `app/api/v1/*` |
| Bot | Telegram inbound handling and moderation | `app/bot/*` |
| Content AI | trend discovery, prompts, images, dedupe, queue | `app/services/content_engine.py` |
| Moderation | deterministic checks + LLM classification + reputation | `app/services/moderation.py` |
| Analytics | event stream and strategy signals | `app/services/analytics.py` |
| Workers | scheduler, publishing, autonomous cycles | `app/workers/*` |

## Autonomous loop

1. Collect public trends from allowed APIs and configured RSS/partner feeds.
2. Score candidates by novelty, audience fit, safety risk and historic engagement.
3. Generate post + image prompt, check duplicate hash, enqueue scheduled content.
4. Publish due content through aiogram while respecting Telegram retry-after limits.
5. Record impressions/reactions/comments/shares as analytics events.
6. Decision engine adapts queue depth, formats, timing and experiments.

## Safety guardrails

- No unsolicited direct messages or mass invitations.
- No fake engagement, credential harvesting, ban evasion, or private scraping.
- Admin-configured channels/groups only.
- Rate-limited API, Telegram retry handling, content deduplication.
- Secret values are environment variables/Kubernetes Secrets, never committed.

## Admin panel contract

A frontend can consume:

- `GET /api/v1/content` for queue management.
- `POST /api/v1/content/generate` for AI generation.
- `POST /api/v1/content/{id}/approve` for manual override.
- `GET /api/v1/analytics/summary` for dashboard KPIs.
- `GET /api/v1/growth/experiments` for compliant growth ideas.

## Scaling strategy

- Scale `api` horizontally behind Nginx/Ingress.
- Scale Celery workers by queues: `strategy`, `publishing`, `moderation`, `analytics`.
- Use PostgreSQL read replicas for analytics dashboards.
- Add pgvector/Qdrant for memory embeddings and semantic dedupe.
- Partition `analytics_events` by month after high volume.
- Use HPA on CPU, queue latency and Redis queue depth.
