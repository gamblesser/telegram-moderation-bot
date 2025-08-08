from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import os

TOKEN = os.getenv("BOT_TOKEN")
MODERATOR_ID = int(os.getenv("MODERATOR_ID"))
GROUP_ID = os.getenv("GROUP_ID")  # Пример: -1001234567890

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await msg.answer("Привет! Напиши, зачем хочешь вступить в группу.")

@dp.message_handler()
async def collect_request(msg: types.Message):
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Принять", callback_data=f"accept_{msg.from_user.id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{msg.from_user.id}")
    )
    text = f"📩 Заявка от @{msg.from_user.username or msg.from_user.first_name}:\n\n{msg.text}"
    await bot.send_message(MODERATOR_ID, text, reply_markup=kb)
    await msg.answer("Спасибо! Ваша заявка отправлена на модерацию.")

@dp.callback_query_handler(lambda c: c.data.startswith('accept_') or c.data.startswith('reject_'))
async def callback_handler(call: types.CallbackQuery):
    action, user_id = call.data.split('_')
    user_id = int(user_id)

    if action == "accept":
        invite = await bot.create_chat_invite_link(
            chat_id=GROUP_ID,
            member_limit=1,
            creates_join_request=False
        )
        join_button = InlineKeyboardMarkup().add(
            InlineKeyboardButton("🚪 Вступить", url=invite.invite_link)
        )
        await bot.send_message(user_id, "✅ Ваша заявка одобрена.", reply_markup=join_button)
        await call.answer("Пользователь принят.")
    else:
        await bot.send_message(user_id, "❌ Ваша заявка отклонена.")
        await call.answer("Пользователь отклонён.")

if __name__ == "__main__":
    executor.start_polling(dp)