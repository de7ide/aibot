from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.orm_query import Database
from keyboards.kb import get_callback_btns
from filter.admin import IsAdmin


admin_router = Router()
admin_router.message.filter(IsAdmin())


class EditMess(StatesGroup):
    waiting_for_text = State()
    wait_for_anal = State()


@admin_router.message(Command('get_users'))
async def get_users(message: Message, db: Database):
    users = await db.get_all_users()
    stats_text = "\n".join([f"{count+1}. @{user.username}: {user.count_token_used} запрос" for count, user in enumerate(users) ] )
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


class EditSub(StatesGroup):
    waiting_choise = State()
    edit_sub = State()
    edit_name = State()
    edit_description = State()
    edit_price = State()
    del_sub = State()


class AddSub(StatesGroup):
    add_name = State()
    add_description = State()
    add_price = State()


@admin_router.message(Command("edit_sub"))
async def edit_sub(message: Message, db: Database, state: FSMContext):
    await state.clear()
    products = await db.get_all_product()
    btns = {f"{count+1}. {product.name}" : f"product_id_{product.id}" for count, product in enumerate(products)}
    dop_btns = {"➕ Добавить тариф" : "add_sub"}
    btns = {**btns, **dop_btns}
    await message.answer("Выберите тариф, который хотите изменить: ",
                         reply_markup=get_callback_btns(btns=btns))
    await state.set_state(EditSub.waiting_choise)


@admin_router.callback_query(F.data == "add_sub")
async def add_sub_pressed(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введите название тарифа...")
    await state.set_state(AddSub.add_name)


@admin_router.message(F.text, AddSub.add_name)
async def edit_sub_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание тарифа....")
    await state.set_state(AddSub.add_description)


@admin_router.message(F.text, AddSub.add_description)
async def edit_sub_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddSub.add_price)
    await message.answer("Введите цену за тариф....")


@admin_router.message(F.text.isdigit(), AddSub.add_price)
async def edit_sub_price(message: Message, state: FSMContext, db: Database):
    await state.update_data(price=message.text)
    data = await state.get_data()

    await db.add_sub(data)
    await message.answer(f"✅Тариф успешно добавлен!")
    await state.clear()



@admin_router.callback_query(F.data.startswith("product_id_"), EditSub.waiting_choise)
async def choise_product_for_choise(callback: CallbackQuery, db: Database, state: FSMContext):
    product_id = callback.data.split("_")[-1]
    await state.update_data(product_id=product_id)
    product = await db.get_product_by_id(product_id=product_id)
    await callback.message.edit_text(f"{product.name}\n\n{product.description}\n\nЦена: <b>{product.price}</b>руб.",
                                     reply_markup=get_callback_btns(btns={"✏️ Изменить наполнение тарифа": f"edit_prod_id_{product_id}",
                                                                          "❌ Удалить тариф": f"del_prod_id_{product_id}"}))
    await state.set_state(EditSub.edit_sub)


@admin_router.callback_query(F.data.startswith("edit_prod_id_"), EditSub.edit_sub)
async def edit_sub_pressed(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введите название тарифа....")


@admin_router.message(F.text, EditSub.edit_sub)
async def edit_sub_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание тарифа....")
    await state.set_state(EditSub.edit_description)


@admin_router.message(F.text, EditSub.edit_description)
async def edit_sub_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(EditSub.edit_price)
    await message.answer("Введите цену за тариф....")


@admin_router.message(F.text.isdigit(), EditSub.edit_price)
async def edit_sub_price(message: Message, state: FSMContext, db: Database):
    await state.update_data(price=message.text)
    data = await state.get_data()

    await db.edit_sub(data)
    await message.answer(f"✅Тариф успешно изменен!")
    await state.clear()


@admin_router.callback_query(F.data.startswith("del_prod_id"), EditSub.edit_sub)
async def dell_sub_pressed(callback: CallbackQuery, db: Database, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    await state.clear()
    await db.dell_sub(produc_id=data['product_id'])
    await callback.message.edit_text(f"✅Тариф успешно удален!")
