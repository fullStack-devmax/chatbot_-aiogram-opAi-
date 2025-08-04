import datetime

from sqlalchemy import select

from database import SessionLocal
from models import User


async def get_or_create_user(telegram_id: int, nickname: str):
    async with SessionLocal() as session:
        result = await session.execute(
            User.__table__.select().where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            user = User(telegram_id=telegram_id, nickname=nickname)
            session.add(user)
            await session.commit()
        return user

async def can_make_request(username: str):
    today = datetime.date.today()

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == username)
        )
        user = result.scalars().first()

        if not user:
            return False

        if user.last_request_date is None or user.last_request_date != today:
            user.request_count = 0
            user.last_request_date = today

        if user.request_count <= 2:
            user.request_count += 1
            await session.commit()
            return True

        return False
