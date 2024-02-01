import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class BotConfig:
    token: str


@dataclass
class Config:
    bot: BotConfig


def load_configs():
    load_dotenv()

    return Config(
        bot=BotConfig(token=os.getenv("TOKEN"))
    )
