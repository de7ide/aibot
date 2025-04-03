import os

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart

from database.orm_query import Database
from config_data import Config, load_config
from services.anthropic_api import process_image


user_router = Router()
config: Config = load_config()

dowload_dir = "downloads"
os.makedirs(dowload_dir, exist_ok=True)


@user_router.message(CommandStart())
async def start_comm(message: Message, db: Database):
    start_text = await db.get_start_message()
    await message.answer(start_text)
    await db.add_user(
        id=message.from_user.id,
        username=message.from_user.username
    )



@user_router.message(F.photo)
async def handle_image(message: Message, db: Database):
    photo = message.photo[-1]
    mess = await db.get_analysis_message()
    await message.answer(mess)
    # Получаем файл
    file_info = await message.bot.get_file(photo.file_id)
    file_path = file_info.file_path
    local_filename = os.path.join("downloads", f"{message.from_user.id}.jpg")

    # Загружаем фото
    await message.bot.download_file(file_path, local_filename)
    #await message.answer("Фото получено! Отправляю в ChatGPT на обработку...")

    # Отправляем фото в ChatGPT API
    response = await process_image(image_url=f"https://api.telegram.org/file/bot{config.tg_bot.token}/{file_info.file_path}")

    if isinstance(response, str):  # Проверяем, является ли ответ текстом
        await message.answer(response)
        await db.add_count_to_token(id=message.from_user.id)
        os.remove(local_filename)
    else:
        message.answer(f"{file_info.file_path}")
        error_text = response.get("error", {}).get("message", "Неизвестная ошибка")
        await message.answer(f"Ошибка: {error_text}")

    # except Exception as e:
    #     await message.answer(f"Произошла ошибка: {str(e)}")
    # file_info = await message.bot.get_file(photo.file_id)
    # file_path = file_info.file_path
    # local_filename = os.path.join("downloads", f"{message.from_user.id}.jpg")

    # await message.bot.download_file(file_path, local_filename)
    # await message.answer("Фото получено! Отправляю в ChatGPT на обработку...")

    # response = await process_image(local_filename, user_id=message.from_user.id)

    # if response:
    #     await message.answer(response)
    # else:
    #     await message.answer(f"Ошибка- {response.status}\n\n {response.text}")
    # file = await message.bot.get_file(photo.file_id)
    # file_path = os.path.join(dowload_dir, "file_1.jpg")

    # file_path = f"downloads/{file.file_path.split('/')[-1]}"

    # await message.bot.download_file(file.file_path, file_path)
    # result = await process_image(file_path, prompt=config.claud.prompt)
    # await message.answer(f"Результат обработки: {result}")
