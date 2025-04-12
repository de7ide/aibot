from typing import List
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
    available_tokens: Mapped[int] = mapped_column(Integer, default=15)
    purchases: Mapped[List['Purchase']] = relationship(
        "Purchase",
        back_populates="user",
        cascade="all, delete-orphan"
    )


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


class Product(Base):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[int]
    purchases: Mapped[List['Purchase']] = relationship(
        "Purchase",
        back_populates="product",
        cascade="all, delete-orphan"
    )


class Purchase(Base):
    __tablename__ = "purchases"

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    price: Mapped[int]
    payment_id: Mapped[str] = mapped_column(unique=True)
    user: Mapped["User"] = relationship("User", back_populates="purchases")
    product: Mapped["Product"] = relationship("Product", back_populates="purchases")
