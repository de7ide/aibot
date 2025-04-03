from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import Database
from filter.admin import IsAdmin


admin_router = Router()
admin_router.message.filter(IsAdmin())


class EditMess(StatesGroup):
    waiting_for_text = State()
    wait_for_anal = State()


@admin_router.message(Command('get_users'))
async def get_users(message: Message, db: Database):
    users = await db.get_all_users()
    stats_text = "\n".join([f"@{user.username}: {user.count_token_used} запрос" for user in users])
    await message.answer(f"📊 Статистика пользователей:\n{stats_text}")



@admin_router.message(Command("set_start"))
async def set_start_handler(message: Message, state: FSMContext):
    """Запуск FSM для изменения текста /start"""

    await state.set_state(EditMess.waiting_for_text)
    await message.answer("✏️ Введите новый текст для /start:")


@admin_router.message(EditMess.waiting_for_text)
async def process_new_start_text(message: Message, state: FSMContext, db: Database):
    """Получение нового текста, сохранение в БД и выход из FSM"""
    new_text = message.text.strip()

    await db.update_start_message(new_message=new_text)

    await state.clear()
    await message.answer("✅ Приветственное сообщение успешно обновлено!")


@admin_router.message(Command("set_message"))
async def set_anal_handler(message: Message, state: FSMContext):
    """Запуск FSM для изменения текста /start"""

    await state.set_state(EditMess.wait_for_anal)
    await message.answer("✏️ Введите новый текст перед анализом...")


@admin_router.message(EditMess.wait_for_anal)
async def set_anal_mess(message: Message, state: FSMContext, db: Database):
    """Получение нового текста, сохранение в БД и выход из FSM"""
    new_text = message.text.strip()

    await db.update_analysis_message(new_message=new_text)

    await state.clear()
    await message.answer("✅ Cообщение перед анализом успешно обновлено!")