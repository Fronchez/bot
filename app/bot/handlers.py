"""Telegram bot handlers."""

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from sqlalchemy import select

from app.db.session import AsyncSessionFactory
from app.models.user import TelegramUser
from app.services.giveaways import GiveawayService
from app.services.moderation import ModerationService
from app.services.referrals import ReferralService

router = Router()
moderation = ModerationService()


@router.message(CommandStart())
async def start(message: Message) -> None:
    """Welcome new users."""
    await message.answer("Привет! Я AI-бот сообщества: публикую полезное, модерирую и запускаю активности 🤖")


@router.message(Command("leaderboard"))
async def leaderboard(message: Message) -> None:
    """Show activity leaderboard."""
    async with AsyncSessionFactory() as session:
        leaders = await ReferralService(session).leaderboard(limit=10)
    if not leaders:
        await message.answer("Пока нет рейтинга активности. Напиши полезный комментарий и стань первым 🏆")
        return
    text = "🏆 Рейтинг активности\n\n" + "\n".join(
        f"{idx}. @{row['username'] or row['telegram_id']} — {row['points']} очков"
        for idx, row in enumerate(leaders, start=1)
    )
    await message.answer(text)


@router.message(Command("giveaways"))
async def active_giveaways(message: Message) -> None:
    """Show active giveaways."""
    async with AsyncSessionFactory() as session:
        giveaways = await GiveawayService(session).active()
    if not giveaways:
        await message.answer("Сейчас активных розыгрышей нет. Следи за анонсами 🎁")
        return
    await message.answer(
        "🎁 Активные розыгрыши\n\n"
        + "\n".join(f"• {giveaway.title}: {giveaway.prize}" for giveaway in giveaways)
    )


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
