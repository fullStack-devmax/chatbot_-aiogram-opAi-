from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import Router, F

from sqlalchemy import select

from database import SessionLocal
from models import User, Request


cmd_router = Router()


@cmd_router.message(Command("start"))
async def start_cmd(message: Message):
    async with SessionLocal() as session:
        username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalars().first()

        if not user:
            user = User(username=username, firstname=message.from_user.first_name)
            session.add(user)
            await session.commit()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_english")],
        [InlineKeyboardButton(text="🇷🇺 Russian", callback_data="lang_russian")],
        [InlineKeyboardButton(text="🇺🇿 Uzbek", callback_data="lang_uzbek")]
    ])

    await message.answer(
        "👋 Welcome! You can send only 3 messages per day.\n\n"
        "🌐 Please choose your language:",
        reply_markup=keyboard
    )



@cmd_router.message(Command("language"))
async def choose_language(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_english")],
        [InlineKeyboardButton(text="🇷🇺 Russian", callback_data="lang_russian")],
        [InlineKeyboardButton(text="🇺🇿 Uzbek", callback_data="lang_uzbek")]
    ])
    await message.answer("🌐 Choose your language:", reply_markup=keyboard)

@cmd_router.message(Command("english"))
async def set_english(message: Message):
    await set_language_callback(message, "english")

@cmd_router.message(Command("russian"))
async def set_russian(message: Message):
    await set_language_callback(message, "russian")

@cmd_router.message(Command("uzbek"))
async def set_uzbek(message: Message):
    await set_language_callback(message, "uzbek")

@cmd_router.callback_query()
async def set_language_callback(callback: CallbackQuery):
    if callback.data.startswith("lang_"):
        lang = callback.data.split("_")[1]

        username = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.first_name

        async with SessionLocal() as session:
            result = await session.execute(select(User).where(User.username == username))
            user = result.scalars().first()
            if user:
                user.language = lang
                await session.commit()
                await callback.answer(f"✅ Language set to {lang.capitalize()}", show_alert=True)
                await callback.answer("Nima mavzuda savolingiz bor?")
            else:
                await callback.answer("⚠️ Please use /start first to register.", show_alert=True)

@cmd_router.message(Command("users"))
async def list_users(message: Message):
    async with SessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"DEBUG: Found {len(users)} users in DB")


        if not users:
            await message.answer("⚠️ No users found.")
            return

        buttons = [
            [InlineKeyboardButton(
                text=f"{user.firstname} ({user.username})",
                callback_data=f"view_user:{user.id}"
            )]
            for user in users
        ]

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer("👥 Select a user to view their requests:", reply_markup=keyboard)


@cmd_router.callback_query(F.data.startswith("view_user:"))
async def view_user_requests(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])

    async with SessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            await callback.message.answer("⚠️ User not found.")
            return

        result = await session.execute(
            select(Request).where(Request.user_id == user_id).order_by(Request.created_at.desc())
        )
        requests = result.scalars().all()
        print(f"Found {len(requests)} requests for user {user_id}")

        if not requests:
            await callback.message.answer(f"👤 {user.firstname} ({user.username}) has no requests yet.")
            return

        response = f"📜 Requests from {user.firstname} ({user.username}):\n\n"
        for r in requests:
            response += f"🕒 {r.created_at.strftime('%Y-%m-%d %H:%M')}\n💬 {r.question}\n\n"

        await callback.message.answer(response)
