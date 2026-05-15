"""Telegram bot handlers."""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import select

from app.db.session import AsyncSessionFactory
from app.models.user import TelegramUser
from app.services.moderation import ModerationService

router = Router()
moderation = ModerationService()


@router.message(CommandStart())
async def start(message: Message) -> None:
    """Welcome new users."""
    await message.answer("Привет! Я AI-бот сообщества: публикую полезное, модерирую и запускаю активности 🤖")


@router.message()
async def moderate_message(message: Message) -> None:
    """Moderate incoming group messages."""
    text = message.text or message.caption or ""
    if not text:
        return
    async with AsyncSessionFactory() as session:
        user = await session.scalar(
            select(TelegramUser).where(
                TelegramUser.telegram_id == (message.from_user.id if message.from_user else 0)
            )
        )
        reputation = user.reputation if user else 0
    decision = await moderation.classify(text, reputation)
    if decision.action in {"delete", "ban"}:
        await message.delete()
    elif decision.action == "warn":
        await message.reply("⚠️ Пожалуйста, без спама, токсичности и сомнительных ссылок.")
