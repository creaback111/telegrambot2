import asyncio
import calendar
from datetime import datetime
import requests

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command

# --- Токени ---
TOKEN = "8731706330:AAGxJ3fXtbHU3PMdHqHXmjHT96RrIzW4G9M"
OTHER_BOT_TOKEN = "8628899910:AAEt3SHIWCSyOuTsoDJuWcq5tzkjD3W-Ac0"
OTHER_BOT_CHAT_ID = "-1003481101155"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- БАЗА ---
bookings = []
user_data = {}

# --- КНОПКИ ---
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Записатися")],
        [KeyboardButton(text="💸 Прайс"), KeyboardButton(text="📸 Instagram")]
    ],
    resize_keyboard=True
)

services_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Корекція брів"), KeyboardButton(text="Корекція + фарбування")],
        [KeyboardButton(text="Ламінування брів"), KeyboardButton(text="Ламінування + фарбування")],
        [KeyboardButton(text="Депіляція верхньої губи"), KeyboardButton(text="Носова депіляція")]
    ],
    resize_keyboard=True
)

# --- КАЛЕНДАР ---
def generate_calendar(year=None, month=None):
    now = datetime.now()
    year = year or now.year
    month = month or now.month

    kb = InlineKeyboardMarkup(inline_keyboard=[])
    kb.inline_keyboard.append([InlineKeyboardButton(text=f"{month:02}/{year}", callback_data="ignore")])
    days = ["Пн","Вт","Ср","Чт","Пт","Сб","Нд"]
    kb.inline_keyboard.append([InlineKeyboardButton(text=day, callback_data="ignore") for day in days])

    cal = calendar.monthcalendar(year, month)
    for week in cal:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                row.append(InlineKeyboardButton(text=str(day), callback_data=f"date_{year}_{month}_{day}"))
        kb.inline_keyboard.append(row)

    kb.inline_keyboard.append([InlineKeyboardButton(text="⬅ Назад", callback_data="back")])
    return kb

# --- СТАРТ ---
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Привіт 💖 Обери опцію:", reply_markup=main_kb)
    await bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEBY_hg3xPq7F8Zzr7D8YJ0tF2kW3F0uAACRAADwDZPE7IkXLh0zH8gHgQ")

# --- ІНСТА ---
@dp.message(lambda m: m.text == "📸 Instagram")
async def insta(message: types.Message):
    await message.answer("https://instagram.com/yourpage")
    await bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEBY_1g3xSPP1sV3YwX0tLQfWkeX6n0QACXQADwDZPE5eN-bA3RLZMGgQ")

# --- ПРАЙС ---
@dp.message(lambda m: m.text == "💸 Прайс")
async def price(message: types.Message):
    await message.answer(
        "💸 Прайс:\n\n"
        "Корекція брів — 150 грн\n"
        "Корекція + фарбування — 250 грн\n"
        "Ламінування брів — 300 грн\n"
        "Ламінування + фарбування — 350 грн\n"
        "Депіляція верхньої губи — 50 грн\n"
        "Носова депіляція — 100 грн"
    )
    await bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEBY_5g3xYcG1vQ5W-Z2mT5R8K8YHhU0wACaQADwDZPE6f3Yh6xo0N7yGgQ")

# --- ЗАПИС ---
@dp.message(lambda m: m.text == "📅 Записатися")
async def booking(message: types.Message):
    await message.answer("Оберіть дату:", reply_markup=generate_calendar())
    await bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEBY_9g3xbr1q3yA3Rv6r5A6nF8k0lQhwACeQADwDZPE7pF3oYxCghlGgQ")

# --- ВИБІР ДАТИ ---
@dp.callback_query(F.data.startswith("date_"))
async def select_date(callback: types.CallbackQuery):
    _, year, month, day = callback.data.split("_")
    date = f"{day}.{month}.{year}"

    if any(b["date"] == date for b in bookings):
        await callback.answer("❌ Ця дата зайнята", show_alert=True)
        return

    user_data[callback.from_user.id] = {"date": date}
    await callback.message.answer("Введіть ім’я та прізвище:")
    await bot.send_sticker(callback.from_user.id, "CAACAgIAAxkBAAEBaAFg3yW5Y6wnSg2vlhLwX_sXQk3f-QACQQADwDZPE7GHN1kDk4x8GgQ")
    await callback.answer()

# --- ОБРОБКА ВВОДУ ---
@dp.message()
async def process(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        return
    data = user_data[user_id]

    if "name" not in data:
        data["name"] = message.text
        await message.answer("Введіть номер телефону:")
        await bot.send_sticker(user_id, "CAACAgIAAxkBAAEBaQFg3yW9bvhQY4ZqQpHtR0qa5JvO_AACRAADwDZPE7Ifn_vc4OqzGgQ")
        return

    if "phone" not in data:
        data["phone"] = message.text
        await message.answer("Оберіть послугу:", reply_markup=services_kb)
        await bot.send_sticker(user_id, "CAACAgIAAxkBAAEBaQFg3yW9bvhQY4ZqQpHtR0qa5JvO_AACRAADwDZPE7Ifn_vc4OqzGgQ")
        return

    if "service" not in data:
        data["service"] = message.text
        username = message.from_user.username or "немає"
        booking_data = {
            "date": data["date"],
            "name": data["name"],
            "phone": data["phone"],
            "service": data["service"],
            "username": username,
            "user_id": user_id
        }
        bookings.append(booking_data)

        # --- Надсилаємо в інший бот ---
        text = (
            f"📥 Новий запис!\n\n"
            f"📅 Дата: {data['date']}\n"
            f"👤 Ім’я: {data['name']}\n"
            f"📞 Телефон: {data['phone']}\n"
            f"💼 Послуга: {data['service']}\n"
            f"📛 {username}"
        )
        url = f"https://api.telegram.org/bot{OTHER_BOT_TOKEN}/sendMessage?chat_id={OTHER_BOT_CHAT_ID}&text={text}"
        requests.get(url)

        # --- Inline кнопка Відмінити ---
        cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Відмінити запис", callback_data=f"cancel_{len(bookings)-1}")]
        ])
        await message.answer(
            f"✅ Ви записані!\n\n"
            f"📅 Дата: {data['date']}\n"
            f"👤 Ім’я: {data['name']}\n"
            f"📞 Телефон: {data['phone']}\n"
            f"💼 Послуга: {data['service']}",
            reply_markup=cancel_kb
        )
        await bot.send_sticker(user_id, "CAACAgIAAxkBAAEBaQFg3yW9bvhQY4ZqQpHtR0qa5JvO_AACRAADwDZPE7Ifn_vc4OqzGgQ")
        del user_data[user_id]

# --- Обробка скасування ---
@dp.callback_query(F.data.startswith("cancel_"))
async def cancel_booking(callback: types.CallbackQuery):
    index = int(callback.data.split("_")[1])
    if 0 <= index < len(bookings):
        canceled = bookings.pop(index)

        # --- Надсилаємо в інший бот ---
        text = (
            f"❌ Запис скасовано!\n\n"
            f"📅 Дата: {canceled['date']}\n"
            f"👤 Ім’я: {canceled['name']}\n"
            f"📞 Телефон: {canceled['phone']}\n"
            f"💼 Послуга: {canceled['service']}\n"
            f"📛 {canceled['username']}"
        )
        url = f"https://api.telegram.org/bot{OTHER_BOT_TOKEN}/sendMessage?chat_id={OTHER_BOT_CHAT_ID}&text={text}"
        requests.get(url)

        await callback.message.edit_text(f"❌ Ваш запис на {canceled['date']} скасовано!")
        await callback.answer("Запис скасовано ✅")
        await bot.send_sticker(callback.from_user.id, "CAACAgIAAxkBAAEBaQFg3yW9bvhQY4ZqQpHtR0qa5JvO_AACRAADwDZPE7Ifn_vc4OqzGgQ")

# --- ЗАПУСК ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())