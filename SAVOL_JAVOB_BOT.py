import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

# O'zingning tokening
API_TOKEN = '9175839146:AAGh4k4PVSONbSOIF9G251_Ny9Wkr9JDnrM'

# O'zining Telegram ID raqamingni shu yerga yozasan (faqat o'zing admin bo'lishing uchun)
ADMIN_ID = 8712944673  # <--- O'z ID raqamingni yozishni unutma!

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=storage)

class AdminState(StatesGroup):
    waiting_for_broadcast = State()

class UserState(StatesGroup):
    waiting_for_answer = State()

# 1. /start buyrug'i
@dp.message(F.text == '/start')
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "Salom Admin! Guruhga yoki obunachilarga savol yuborish uchun /send buyrug'ini yuboring."
        )
    else:
        await message.answer(
            "Salom! Bu yerda anonim savol-javob boti. Savolga javob berish uchun /ask buyrug'ini bosing."
        )

# 2. Admin savol yuborishni boshlashi uchun /send
@dp.message(F.text == '/send')
async def cmd_send(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Bu buyruq faqat admin uchun!")
        return
    
    await state.set_state(AdminState.waiting_for_broadcast)
    await message.answer("Obunachilarga yubormoqchi bo'lgan savolingizni yozib yuboring:")

# 3. Admin yozgan savolni qabul qilib saqlash (hozircha oddiy holatda)
@dp.message(AdminState.waiting_for_broadcast)
async def process_broadcast(message: types.Message, state: FSMContext):
    question_text = message.text
    await state.clear()
    await message.answer(f"Savol qabul qilindi! (Hozircha test rejimida ishlayapti)")

# 4. Foydalanuvchi javob yozishni boshlashi uchun /ask
@dp.message(F.text == '/ask')
async def cmd_ask(message: types.Message, state: FSMContext):
    await state.set_state(UserState.waiting_for_answer)
    await message.answer("Savolingizni yoki javobingizni yuboring, uni faqat admin ko'radi:")

# 5. Foydalanuvchidan kelgan xabarni faqat adminga yuborish
@dp.message(UserState.waiting_for_answer)
async def receive_user_answer(message: types.Message, state: FSMContext):
    user_answer = message.text
    await state.clear()
    
    # Javobni adminga yuboramiz
    try:
        await bot.send_message(
            ADMIN_ID,
            f"📩 **Yangi anonim javob keldi:**\n\n{user_answer}"
        )
        await message.answer("Javobingiz admingacha anonim tarzda yetkazildi! Rahmat.")
    except Exception as e:
        await message.answer("Xatolik yuz berdi, keyinroq urinib ko'ring.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

