from aiogram import Router
from aiogram.types import CallbackQuery
from sqlalchemy import select
from database import SessionLocal
from models import User, Request

user_router = Router()

@user_router.callback_query()
async def show_user_requests(callback: CallbackQuery):
    if callback.data.startswith("user_"):
        selected_user_id = int(callback.data.split(":", 1)[1])

    async with SessionLocal() as session:
        result = await session.execute(
            select(Request).where(Request.user_id == selected_user_id).order_by(Request.created_at.desc())
        )
        user_requests = result.scalars().all()

        if not user_requests:
            await callback.message.answer(f"📭 No requests found for {selected_user_id}.")
            return

        await callback.message.answer(f"📝 Requests by {selected_user_id}:")
        for req in user_requests:
            await callback.message.answer(
                f"💬 *Question:* {req.question}\n"
                f"🕒 _Asked at: {req.created_at.strftime('%Y-%m-%d %H:%M')}_",
                parse_mode="Markdown"
            )

        await callback.answer()
