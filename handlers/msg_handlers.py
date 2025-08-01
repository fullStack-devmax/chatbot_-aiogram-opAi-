from openai import OpenAI

from aiogram import Router, types

from sqlalchemy import select

from utils.user_utils import can_make_request
from config import OPENAI_API_KEY
from database import SessionLocal
from models import User, Request


msg_router = Router()



client = OpenAI(api_key=OPENAI_API_KEY)

async def ask_openai(prompt: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


@msg_router.message()
async def handle_message(message: types.Message):
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.username == username))
        if not user:
            user = User(username=username, firstname=message.from_user.first_name)
            session.add(user)
            await session.commit()
            await session.refresh(user)

        new_request = Request(
            user_id=user.id,
            question=message.text
        )
        session.add(new_request)
        await session.commit()

    if await can_make_request(username):
        prompt = f"Reply in {user.language}. User: {message.text}"
        reply = await ask_openai(prompt)
        await message.answer(reply)
    else:
        await message.answer("⚠️ Daily limit reached: You can only send 3 requests per day. Try again tomorrow.")

    print(f"user_id={user.id} text={message.text}")
