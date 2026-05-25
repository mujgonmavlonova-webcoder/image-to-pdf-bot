import logging
import os
import re

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from config import settings
from services import convert_images_to_pdf
from utils import build_temp_path, cleanup_files, get_file_size_mb, is_valid_image
from handlers.start import check_subscription, subscribe_keyboard

logger = logging.getLogger(__name__)
router = Router(name="image")

# ── FSM holatlari ─────────────────────────────────────────────────────────────

class ConvertStates(StatesGroup):
    waiting_for_pdf_name = State()   # Foydalanuvchi PDF nomini yozishini kutish


# ── In-memory queue: { user_id: ["/temp/xxx.jpg", ...] } ─────────────────────
_user_queues: dict[int, list[str]] = {}


def _get_queue(user_id: int) -> list[str]:
    return _user_queues.setdefault(user_id, [])


def _clear_queue(user_id: int) -> list[str]:
    return _user_queues.pop(user_id, [])


async def _download_to_temp(bot: Bot, file_id: str, extension: str) -> str:
    dest = build_temp_path(settings.TEMP_DIR, extension)
    tg_file = await bot.get_file(file_id)
    await bot.download_file(tg_file.file_path, dest)
    return dest


def _safe_filename(name: str) -> str:
    """Foydalanuvchi kiritgan nomdan xavfsiz fayl nomi yasash."""
    name = name.strip()
    name = re.sub(r"[^\w\s\-]", "", name, flags=re.UNICODE)
    name = re.sub(r"\s+", "_", name)
    return name[:64] or "document"


# ── Obuna callback ────────────────────────────────────────────────────────────

@router.callback_query(F.data == "check_sub")
async def callback_check_sub(call: CallbackQuery, bot: Bot) -> None:
    user_id = call.from_user.id
    subscribed = await check_subscription(bot, user_id)

    if subscribed:
        await call.message.edit_text(
            "✅ <b>Rahmat! Obuna tasdiqlandi.</b>\n\n"
            "Endi menga rasm(lar) yuboring, men ularni PDF ga aylantirib beraman! 🖼→📄\n\n"
            "Rasmlar yuborib bo'lgach /convert buyrug'ini yuboring.",
            parse_mode="HTML",
        )
    else:
        await call.answer(
            "❌ Siz hali obuna bo'lmagansiz! Iltimos, avval kanalga obuna bo'ling.",
            show_alert=True,
        )


# ── Har qanday shakldagi rasmlarni qabul qilish (Photo va Document) ──────────

@router.message(F.photo | F.document)
async def handle_incoming_image(message: Message, bot: Bot, state: FSMContext) -> None:
    user_id = message.from_user.id

    # Obuna tekshirish
    if not await check_subscription(bot, user_id):
        await message.reply(
            "⚠️ Botdan foydalanish uchun avval kanalga obuna bo'ling!",
            reply_markup=subscribe_keyboard(),
        )
        return

    # PDF nomi kiritilishi kutilayotgan bo'lsa, rasm qabul qilmaymiz
    current_state = await state.get_state()
    if current_state == ConvertStates.waiting_for_pdf_name:
        await message.reply(
            "✏️ Iltimos, avval PDF fayl nomini kiriting yoki /cancel ni yuboring."
        )
        return

    queue = _get_queue(user_id)

    # Maksimal rasmlar sonini tekshirish
    if len(queue) >= settings.MAX_IMAGES_PER_SESSION:
        await message.reply(
            f"⚠️ Navbat to'ldi ({settings.MAX_IMAGES_PER_SESSION} ta rasm).\n"
            "/convert yuboring yoki /cancel bilan tozalang.",
        )
        return

    file_id = ""
    ext = ".jpg"
    file_size = 0

    # 1-Ssenariy: Srazu kameradan olingan yoki oddiy rasm (Photo)
    if message.photo:
        photo = message.photo[-1]  # Eng sifatli o'lchami
        file_id = photo.file_id
        file_size = photo.file_size or 0
        ext = ".jpg"

    # 2-Ssenariy: Sifatni yo'qotmaslik uchun fayl shaklida yuborilgan rasm (Document)
    elif message.document:
        doc = message.document
        filename = doc.file_name or ""
        mime = doc.mime_type or ""

        if not is_valid_image(filename, mime):
            await message.reply(
    "❌ Fayl turi qo'llab-quvvatlanmaydi.\n"
                "Faqat <b>JPG, JPEG yoki PNG</b> formatdagi rasmlar yuborilsin.",
                parse_mode="HTML",
            )
            return

        file_id = doc.file_id
        file_size = doc.file_size or 0
        ext = os.path.splitext(filename.lower())[1] or ".jpg"

    # Hajmni tekshirish
    size_mb = get_file_size_mb(file_size)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        await message.reply(
            f"❌ Rasm juda katta ({size_mb:.1f} MB). Maksimal: {settings.MAX_FILE_SIZE_MB} MB."
        )
        return

    status_msg = await message.reply("⬇️ Yuklanmoqda…")

    try:
        path = await _download_to_temp(bot, file_id, ext)
        queue.append(path)
    except Exception as exc:
        logger.exception("Download failed for user %d", user_id)
        await status_msg.edit_text(f"❌ Rasmni yuklab bo'lmadi: {exc}")
        return

    count = len(queue)
    await status_msg.edit_text(
        f"✅ <b>{count}-rasm</b> navbatga qo'shildi.\n\n"
        f"📤 Yana rasm yuboring yoki /convert ni bosing.",
        parse_mode="HTML",
    )


# ── /convert — PDF nomini so'rash ─────────────────────────────────────────────

@router.message(Command("convert"))
async def cmd_convert(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    queue = _get_queue(user_id)

    if not queue:
        await message.reply(
            "📭 Navbat bo'sh.\n"
            "Avval menga rasm(lar) yuboring, keyin /convert yuboring."
        )
        return

    count = len(queue)
    await state.set_state(ConvertStates.waiting_for_pdf_name)
    await message.reply(
        f"📝 <b>{count} ta rasm</b> tayyor.\n\n"
        "PDF fayl uchun <b>nom kiriting</b> (masalan: <code>mening_hujjatim</code>):\n\n"
        "<i>Bekor qilish uchun /cancel yuboring.</i>",
        parse_mode="HTML",
    )


# ── PDF nomini qabul qilib, konvertatsiya qilish ─────────────────────────────

@router.message(ConvertStates.waiting_for_pdf_name)
async def receive_pdf_name(message: Message, bot: Bot, state: FSMContext) -> None:
    user_id = message.from_user.id

    if message.text and message.text.strip().startswith("/"):
        await state.clear()
        await message.reply("❌ Bekor qilindi.")
        return

    raw_name = message.text or ""
    pdf_name = _safe_filename(raw_name)

    if not pdf_name or pdf_name == "document" and not raw_name.strip():
        await message.reply(
            "⚠️ Noto'g'ri nom. Iltimos, harf yoki raqamlardan iborat nom kiriting."
        )
        return

    queue = _get_queue(user_id)
    if not queue:
        await state.clear()
        await message.reply("📭 Navbat bo'shalib qoldi. Iltimos, qaytadan rasm yuboring.")
        return

    image_count = len(queue)
    image_paths = list(queue)
    pdf_path = build_temp_path(settings.TEMP_DIR, ".pdf")
    final_filename = f"{pdf_name}.pdf"

    status_msg = await message.reply(
        f"⚙️ <b>{image_count} ta rasm</b> PDF ga aylantirilmoqda…\n"
        f"📄 Fayl nomi: <code>{final_filename}</code>",
        parse_mode="HTML",
    )

    await state.clear()

    try:
        await convert_images_to_pdf(image_paths, pdf_path)

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        pdf_doc = BufferedInputFile(pdf_bytes, filename=final_filename)
        await status_msg.edit_text("📤 PDF yuklanmoqda…")
        await message.answer_document(
            document=pdf_doc,
            caption=(
                f"✅ <b>PDF tayyor!</b>\n"
                f"📄 Fayl: <code>{final_filename}</code>\n"
                f"🖼 Rasmlar soni: <b>{image_count}</b>"
            ),
            parse_mode="HTML",
        )
        await status_msg.delete()

    except Exception as exc:
        logger.exception("PDF conversion failed for user %d", user_id)
        await status_msg.edit_text(
            f"❌ Xatolik yuz berdi: <code>{exc}</code>\n\n"
            "Qaytadan urinib ko'ring yoki /cancel yuboring.",
            parse_mode="HTML",
        )
    finally:
      cleanup_files(*image_paths, pdf_path)
        _clear_queue(user_id)


# ── /cancel ───────────────────────────────────────────────────────────────────

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    leftover = _clear_queue(user_id)
    cleanup_files(*leftover)
    await state.clear()

    if leftover:
        await message.reply(
            f"🗑 Navbat tozalandi. {len(leftover)} ta rasm o'chirildi.\n"
            "Qayta boshlashingiz mumkin!"
        )
    else:
        await message.reply("ℹ️ Navbat allaqachon bo'sh edi.")


# ── Noma'lum xabarlar ─────────────────────────────────────────────────────────

@router.message()
async def handle_unknown(message: Message) -> None:
    await message.reply(
        "🤔 Men faqat rasmlar va buyruqlarni tushunaman.\n"
        "JPG/PNG rasm yuboring yoki /help ni bosing."
    )
