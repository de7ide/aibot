import asyncio
import os

from aiogram import Bot, Router, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import CommandStart

from database.orm_query import Database
from config_data import Config, load_config
from keyboards.kb import get_callback_btns, get_payment_kb
from services.anthropic_api import process_image


user_router = Router()
config: Config = load_config()

dowload_dir = "downloads"
os.makedirs(dowload_dir, exist_ok=True)


class WaitState(StatesGroup):
    wait_photo = State()


class BuyingState(StatesGroup):
    choise_tarif = State()


@user_router.message(CommandStart())
async def start_comm(message: Message, db: Database, state: FSMContext):
    await state.clear()
    start_text = await db.get_start_message()
    await message.answer(start_text)
    await db.add_user(
        id=message.from_user.id,
        username=message.from_user.username
    )


@user_router.message(F.photo)
async def handle_image(message: Message, db: Database, state: FSMContext):
    await state.clear()
    photo = message.photo[-1]
    # Получаем из бд сообщение пред анализом
    analisis_mess = await db.get_analysis_message()
    # Получаем из бд токены для исползования(при добавлении юзера впервые, используются как пробные попытки)
    tokens = await db.get_available_tokens(message.from_user.id)

    # Получаем файл
    file_info = await message.bot.get_file(photo.file_id)
    file_path = file_info.file_path
    local_filename = os.path.join("downloads", f"{message.from_user.id}.jpg")
    await state.update_data(file_info=file_info)

    # Загружаем фото
    await message.bot.download_file(file_path, local_filename)

    # Если available_token у юзера будет больше 0, то бот делает анализ изображения
    if tokens > 0:
        await message.answer(analisis_mess)
        # Отправляем фото в ChatGPT API
        response = await process_image(image_url=f"https://api.telegram.org/file/bot{config.tg_bot.token}/{file_info.file_path}")

        # Проверяем, является ли ответ текстом
        if isinstance(response, str):
            await message.answer(response, reply_markup=get_callback_btns(btns={
                "Еще мнение" : "another_opinion"}))
            # С каждым запросом счетчик count_to_token возрастает на 1, а available_token уменьшается на 1
            await db.add_count_to_token(id=message.from_user.id)
        else:
            error_text = response.get("error", {}).get("message", "Неизвестная ошибка")
            await message.answer(f"Ошибка: {error_text}")

    # Если available_token = 0, то мы вызываем окно с выбором подписки
    else:
        # Получение всех вариантов подписки из бд
        products = await db.get_all_product()
        # Создание инлайн кнопок подписок
        btns = {product.name : f"product_id_{product.id}" for product in products}
        await state.set_state(BuyingState.choise_tarif)
        await message.answer("Дорогой друг! Я так рад, что тебе понравились мои описания искусства! Поддержи мою работу небольшим бонусом, мне будет очень приятно 🙏 и мои создатели смогут закрывать расходы, на мое содержание.",
                             reply_markup=get_callback_btns(btns=btns))


# Обработчик нажатия кнопки "Еще мнение"
@user_router.callback_query(F.data == "another_opinion")
async def another_opinion_pressed(callback: CallbackQuery, db: Database, state: FSMContext):
    await callback.answer()
    # Получаем словарь, в который мы на предыдущем шаге сохраняли "file_path"
    data = await state.get_data()
    file_info = data.get("file_info")
    # Сообщение перед анализом(из БД)
    analysis_mess = await db.get_analysis_message()
    # Токены доступа(из БД)
    tokens = await db.get_available_tokens(callback.from_user.id)

    await callback.message.bot.download_file(file_info.file_path, f"downloads/{callback.from_user.id}.jpg")
    # Делаем проверку, что и в обработчике фото
    if tokens > 0:
        await callback.message.answer(analysis_mess)
        # Отправляем фото в ChatGPT API
        response = await process_image(image_url=f"https://api.telegram.org/file/bot{config.tg_bot.token}/{file_info.file_path}")

        # Проверяем, является ли ответ текстом
        if isinstance(response, str):
            await callback.message.answer(response)
            await db.add_count_to_token(id=callback.from_user.id)
        else:
            error_text = response.get("error", {}).get("message", "Неизвестная ошибка")
            await callback.message.answer(f"Ошибка: {error_text}")

    # Если available_token = 0, то мы вызываем окно с выбором подписки
    else:
        # Получение всех вариантов подписки из бд
        products = await db.get_all_product()
        # Создание инлайн кнопок подписок
        btns = {product.name : f"product_id_{product.id}" for product in products}
        await state.set_state(BuyingState.choise_tarif)
        await callback.message.answer("Дорогой друг! Я так рад, что тебе понравились мои описания искусства! Поддержи мою работу небольшим бонусом, мне будет очень приятно 🙏 и мои создатели смогут закрывать расходы, на мое содержание.",
                                    reply_markup=get_callback_btns(btns=btns))


# Обработчик кнопки тарифа, выбираемый пользователем
@user_router.callback_query(F.data.startswith("product_id_"), BuyingState.choise_tarif)
async def choise_product_button(callback: CallbackQuery, db: Database):
    product_id = callback.data.split("_")[-1]
    product = await db.get_product_by_id(product_id=product_id)
    await callback.message.edit_text(f"Приобрести пакет запросов:\n\n{product.description}\n\nЦена: <b>{product.price}</b>руб.",
                                     reply_markup=get_callback_btns(btns={"Оплатить": f"buy_{product_id}_{product.price}"}))

# Обработчик кнопки оплаты тарфа
@user_router.callback_query(F.data.startswith("buy_"))
async def buy_product_press(callback: CallbackQuery, db: Database, bot: Bot, state: FSMContext):
    await state.clear()
    # Загружаем юзера из бд
    user_info = await db.get_user_by_id(user_id=callback.from_user.id)
    _, product_id, price = callback.data.split('_')
    # Отправляем инвойс оплаты
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=f"Оплата {price}₽",
        description=f"Завершите оплату, в размере {price}₽, чтобы продолжить пользоваться Артии",
        payload=f"{user_info.id}_{product_id}",
        provider_token=config.tg_bot.yookassa,
        currency="RUB",
        prices=[LabeledPrice(
            label=f"Оплата {price}",
            amount=int(price) * 100
        )],
        reply_markup=get_payment_kb(price=price)
    )
    await callback.message.delete()


@user_router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@user_router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message, db: Database):
    payment_info = message.successful_payment
    user_id, product_id, = payment_info.invoice_payload.split('_')
    payment_data = {
        "user_id": int(user_id),
        "payment_id": payment_info.telegram_payment_charge_id,
        "price": payment_info.total_amount / 100,
        "product_id": int(product_id)
    }
    await db.add_purchase(data=payment_data)
    product_data = await db.get_product_by_id(product_id=product_id)

    product_text = (
        f"🎉 <b>Спасибо за покупку!</b>\n\n"
        f"🛒 <b>Информация о вашем товаре:</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔹 <b>Название:</b> <b>{product_data.name}</b>\n"
        f"🔹 <b>Описание:</b>\n<i>{product_data.description}</i>\n"
        f"🔹 <b>Цена:</b> <b>{product_data.price} ₽</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
    )
    await db.set_available_token(user_id=message.from_user.id, tokens=2)
    await message.answer(
        text=product_text
    )