import typing
from dataclasses import dataclass

import dotenv

if typing.TYPE_CHECKING:
    from app.web.app import Application


@dataclass
class AppConfig:
    debug: bool


@dataclass
class AdminConfig:
    email: str
    password: str


@dataclass
class BotConfig:
    token: str


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    database: str = "project"


@dataclass
class SessionConfig:
    key: str


@dataclass
class Config:
    admin: AdminConfig
    app: AppConfig
    bot: BotConfig
    database: DatabaseConfig
    session: SessionConfig


def setup_config(app: "Application"):
    env_dict = dotenv.dotenv_values(".env")

    app.config = Config(
        admin=AdminConfig(
            email=env_dict["ADMIN_EMAIL"],
            password=env_dict["ADMIN_PASS"],
        ),
        app=AppConfig(debug=env_dict["DEBUG"] == "true"),
        bot=BotConfig(
            token=env_dict["BOT_TOKEN"],
        ),
        database=DatabaseConfig(
            database=env_dict["PG_DB"],
            host=env_dict["PG_HOST"],
            port=env_dict["PG_PORT"],
            user=env_dict["PG_USER"],
            password=env_dict["PG_PASS"],
        ),
        session=SessionConfig(
            key=env_dict["SESSION_KEY"],
        ),
    )

    app.logger.debug(app.config)
