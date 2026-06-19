import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = os.getenv("BOT_TOKEN", "8920765990:AAHyAmF41sZ5aDizTVqSPAmEs30iMkg6NLc")
ADMIN_ID = os.getenv("ADMIN_ID", "5200997241")

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class Form(StatesGroup):
    choosing_specialist = State()
    entering_contacts = State()

specialists = {
    "spec_narko": "Нарколог",
    "spec_psycho": "Психотерапевт",
    "spec_psych": "Психолог",
    "spec_question": "Задать вопрос"
}

def get_specialists_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Нарколог", callback_data="spec_narko"),
            InlineKeyboardButton(text="Психотерапевт", callback_data="spec_psycho")
        ],
       [
                InlineKeyboardButton(text="Психолог", callback_data="spec_psych")
            ],
        [
            InlineKeyboardButton(text="Задать вопрос", callback_data="spec_question")
        ]
    ])
    return keyboard

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🏥 Добро пожаловать в Private Clinic!\n\n"
        "Мы специализируемся на психическом здоровье.\n"
        "🔒 Все обращения строго анонимны.\n\n"
        "Выберите специалиста для записи:",
        reply_markup=get_specialists_keyboard()
    )
    await state.set_state(Form.choosing_specialist)

@dp.callback_query(F.data.startswith("spec_"))
async def process_specialist(callback: types.CallbackQuery, state: FSMContext):
    specialist = specialists.get(callback.data, "Специалист")
    await state.update_data(specialist=specialist)
    
    await callback.message.answer(
        f"✅ Вы выбрали: {specialist}\n\n"
        f"Пожалуйста, напишите ваше имя и номер телефона:\n\n"
        f"Пример:\n"
        f"Алексей +7 777 000 00 00"
    )
    await callback.answer()
    await state.set_state(Form.entering_contacts)

@dp.message(Form.entering_contacts)
async def process_contacts(message: types.Message, state: FSMContext):
    data = await state.get_data()
    specialist = data.get("specialist", "Не указан")
    
    # Отправляем уведомление администратору
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📋 Новая заявка — Private Clinic!\n\n"
             f"👨‍⚕️ Специалист: {specialist}\n"
             f"👤 Данные пациента:\n{message.text}\n\n"
             f"📞 Перезвоните пациенту!\n"
             f"Телефон клиники: 8 (777) 038-82-82"
    )
    
    # Отправляем подтверждение пациенту
    await message.answer(
        "✅ Спасибо! Ваша заявка принята.\n\n"
        "Администратор свяжется с вами в рабочее время:\n"
        "⏰ Ежедневно с 10:00 до 18:00\n\n"
        "📍 Адрес: г. Петропавловск, ул. Медведева, 43\n"
        "📞 8 (777) 038-82-82\n\n"
        "🔒 Напоминаем: все обращения анонимны.\n\n"
        "Если хотите записаться ещё раз — нажмите /start"
    )
    
    await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
