from sqlalchemy import ForeignKey, DateTime, String, Integer, Boolean, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)

    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(String, nullable=False)
    count_token_used: Mapped[str] = mapped_column(Integer, default=0)


class Settings(Base):
    __tablename__ = 'settings'

    start_message: Mapped[str] = mapped_column(String, default="Здравствуйте! Я бот-искусствовед,"
    "который может анализировать"
    "произведения искусства.\n\n"
    "Отправьте мне фотографию картины,"
    "скульптуры или другого произведения"
    "искусства, и я проведу профессиональный"
    "искусствоведческий анализ.\n\n"
    "Я могу определить стиль, эпоху, технику,"
    "композицию и другие аспекты")



class SettingsAnalisys(Base):
    __tablename__ = 'settings_analysis'

    analysis_message: Mapped[str] = mapped_column(String)