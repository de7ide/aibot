from aiogram.types import BotCommand


USER_COMMANDS = [
    BotCommand(command="start", description="Запустить бота"),
]

ADMIN_COMMANDS = USER_COMMANDS + [
    BotCommand(command="get_users", description="Получить всех пользователей"),
    BotCommand(command="set_start", description="Изменить приветсвенное сообщение"),
    BotCommand(command="set_message", description="Изменить сообщение перед анализом"),
    BotCommand(command="edit_sub", description="Редактировать тарифы/подписки")
]