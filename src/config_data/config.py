from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    yookassa: str



@dataclass
class ClaudConf:
    api_url: str
    api_key: str
    user: str
    prompt: str


@dataclass
class Config:
    tg_bot: TgBot
    claud: ClaudConf


def load_config() -> Config:
    env = Env()
    env.read_env()
    return Config(
        tg_bot=TgBot(
            token=env("BOT_TOKEN"),
            admin_ids=list(map(int, env.list('ADMIN_IDS'))),
            yookassa=env("YOOKASSA_TOKEN")
        ),
        claud=ClaudConf(
            api_url=env("API_URL"),
            api_key=env("OPENAI_API_KEY"),
            user=env("USER"),
            prompt=env("PROMPT")
        )
    )