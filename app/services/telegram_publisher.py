"""Telegram publishing adapter."""

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramRetryAfter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.content import ContentItem, ContentStatus


class TelegramPublisher:
    """Publishes scheduled content to a configured Telegram channel."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.bot = Bot(token=self.settings.telegram_bot_token) if self.settings.telegram_bot_token else None

    async def publish(self, session: AsyncSession, item: ContentItem) -> ContentItem:
        """Publish a content item and persist Telegram metadata."""
        if self.bot is None or not self.settings.telegram_channel_id:
            item.status = ContentStatus.PUBLISHED
            item.telegram_message_id = 0
            return item
        try:
            if item.image_url:
                message = await self.bot.send_photo(
                    chat_id=self.settings.telegram_channel_id,
                    photo=item.image_url,
                    caption=item.body_markdown,
                    parse_mode=ParseMode.MARKDOWN,
                )
            else:
                message = await self.bot.send_message(
                    chat_id=self.settings.telegram_channel_id,
                    text=item.body_markdown,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=False,
                )
        except TelegramRetryAfter:
            raise
        item.status = ContentStatus.PUBLISHED
        item.telegram_message_id = message.message_id
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item
