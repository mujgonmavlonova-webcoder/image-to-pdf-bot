from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import settings

router = Router(name="start")

CHANNEL_USERNAME = "proekt_mmm"
CHANNEL_LINK = "https://t.me/proekt_mmm"

WELCOME_TEXT = (
    "👋 <b>Assalomu alaykum! Image → PDF Botga xush kelibsiz!</b>\n\n"
    "Men sizning <b>JPG / JPEG / PNG</b> rasmlaringizni bitta PDF faylga aylantirib beraman.\n\n"
    "<b>Qanday foydalanish:</b>\n"
    "1️⃣ Menga rasm(lar) yuboring.\n"
    "2️⃣ /convert buyrug'ini yuboring.\n"
    "3️⃣ PDF fayl nomini kiriting.\n"
    "4️⃣ Tayyor PDF sizga yuboriladi! 📄\n\n"
    "<b>Buyruqlar:</b>\n"
    "• /convert – rasmlarni PDF ga aylantirish\n"
    "• /cancel  – navbatni tozalash\n"
    "• /help    – yordam\n\n"
    f"<i>Chegara: {settings.MAX_IMAGES_PER_SESSION} tagacha rasm, "
    f"har biri {settings.MAX_FILE_SIZE_MB} MB gacha.</i>"
)


async def check_subscription(bot: Bot, user_id: int) -> bool:
    """True – foydalanuvchi kanalga obuna bo'lgan."""
    try:
        member = await bot.get_chat_member(
            chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id
        )
        return member.status not in ("left", "kicked", "banned")
    except Exception:
        # Kanal topilmasa yoki bot admin bo'lmasa — o'tkazib yuborish
        return True


def subscribe_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=CHANNEL_LINK)],
            [InlineKeyboardButton(text="✅ Obuna bo'ldim", callback_data="check_sub")],
        ]
    )


@router.message(Command("start"))
@router.message(Command("help"))
async def cmd_start(message: Message, bot: Bot) -> None:
    user_id = message.from_user.id  # type: ignore[union-attr]
    subscribed = await check_subscription(bot, user_id)

    if not subscribed:
        await message.answer(
            "⚠️ <b>Botdan foydalanish uchun avval kanalga obuna bo'ling!</b>\n\n"
            f"📢 Kanal: {CHANNEL_LINK}\n\n"
            "Obuna bo'lgach <b>✅ Obuna bo'ldim</b> tugmasini bosing.",
            parse_mode="HTML",
            reply_markup=subscribe_keyboard(),
        )
        return

    await message.answer(WELCOME_TEXT, parse_mode="HTML")
