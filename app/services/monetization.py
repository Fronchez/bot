"""Compliant monetization workflow."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import ContentItem, ContentStatus, ContentType
from app.models.growth import CampaignStatus, MonetizationCampaign
from app.services.ai_client import AIClient


class MonetizationService:
    """Turns approved campaigns into transparent sponsored content."""

    def __init__(self, session: AsyncSession, ai: AIClient | None = None) -> None:
        self.session = session
        self.ai = ai or AIClient()

    async def active_campaigns(self) -> list[MonetizationCampaign]:
        """Return campaigns active for the current time window."""
        now = datetime.now(UTC)
        return list(
            await self.session.scalars(
                select(MonetizationCampaign).where(
                    MonetizationCampaign.status == CampaignStatus.ACTIVE,
                    (MonetizationCampaign.starts_at.is_(None) | (MonetizationCampaign.starts_at <= now)),
                    (MonetizationCampaign.ends_at.is_(None) | (MonetizationCampaign.ends_at >= now)),
                )
            )
        )

    async def generate_sponsored_post(self, campaign_id: UUID) -> ContentItem:
        """Generate a disclosed ad post for an active campaign."""
        campaign = await self.session.get(MonetizationCampaign, campaign_id)
        if campaign is None:
            raise ValueError("Campaign not found")
        prompt = f"""
        Write a transparent Telegram sponsored post in Russian.
        Campaign: {campaign.name}
        Brief: {campaign.creative_brief}
        Disclosure must be included exactly: {campaign.disclosure}
        Landing URL: {campaign.landing_url or ''}
        Avoid deceptive claims. Return JSON with title, body_markdown, image_prompt.
        """
        generated = await self.ai.generate_json(prompt)
        title = str(generated.get("title") or campaign.name)[:240]
        body = f"{campaign.disclosure}\n\n{generated.get('body_markdown', campaign.creative_brief)}"
        image_url = await self.ai.generate_image_url(str(generated.get("image_prompt", campaign.name)))
        item = ContentItem(
            content_type=ContentType.AD,
            status=ContentStatus.DRAFT,
            title=title,
            body_markdown=body,
            image_url=image_url,
            source_url=campaign.landing_url,
            dedupe_hash=f"ad:{campaign.id}:{datetime.now(UTC).isoformat()}",
            score=0.5,
            metadata_json={"campaign_id": str(campaign.id), "disclosure": campaign.disclosure},
        )
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item
