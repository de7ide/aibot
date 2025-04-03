from typing import Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Settings, SettingsAnalisys


class Database:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def add_user(self, id: int, username: str) -> None:
        user = await self.session.get(User, id)
        if not user:
            user = User(
                id=id,
                username=username
            )
            self.session.add(user)
        await self.session.commit()


    async def add_count_to_token(self, id: int):
        user_exists = await self.session.execute(
        select(User.id).where(User.id == id))
        if not user_exists.scalar():
            raise ValueError("User not found")  # Или кастомное исключение

    # Атомарное обновление
        query = (
            update(User).where(User.id == id).values(count_token_used=User.count_token_used + 1)
    )

        await self.session.execute(query)
        await self.session.commit()


    async def get_all_users(self):
        query = select(User).order_by(User.count_token_used.desc())
        result = await self.session.execute(query)
        return result.scalars().all()


    async def get_start_message(self):
        """Получение текста команды /start"""
        stmt = select(Settings).limit(1)
        result = await self.session.execute(stmt)
        settings = result.scalar_one_or_none()

        if not settings:
            settings = Settings(start_message="Здравствуйте! Я бот-искусствовед,"
    "который может анализировать"
    "произведения искусства.\n\n"
    "Отправьте мне фотографию картины,"
    "скульптуры или другого произведения"
    "искусства, и я проведу профессиональный"
    "искусствоведческий анализ.\n\n"
    "Я могу определить стиль, эпоху, технику,"
    "композицию и другие аспекты")
            self.session.add(settings)
            await self.session.commit()

        return settings.start_message


    async def update_start_message(self, new_message: str):
        """Обновление текста команды /start"""
        stmt = select(Settings).limit(1)
        result = await self.session.execute(stmt)
        settings = result.scalar_one_or_none()

        if not settings:
            settings = Settings(start_message=new_message)
            self.session.add(settings)
        else:
            settings.start_message = new_message

        await self.session.commit()


    async def get_analysis_message(self):
        """Получение текста перед анализом """
        stmt = select(SettingsAnalisys).limit(1)
        result = await self.session.execute(stmt)
        settings_two = result.scalar_one_or_none()

        if not settings_two:
            settings_two = SettingsAnalisys(analysis_message="Анализирую изображение. Дайте мне 30 секунд ⏰")
            self.session.add(settings_two)
            await self.session.commit()

        return settings_two.analysis_message


    async def update_analysis_message(self, new_message: str):
        """Обновление текста команды /start"""
        stmt = select(SettingsAnalisys).limit(1)
        result = await self.session.execute(stmt)
        settings = result.scalar_one_or_none()

        if not settings:
            settings = Settings(start_message=new_message)
            self.session.add(settings)
        else:
            settings.analysis_message = new_message

        await self.session.commit()
