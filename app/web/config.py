import typing

import dotenv
from pydantic import BaseModel

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AppConfig(BaseModel):
    debug: bool


class AdminConfig(BaseModel):
    email: str
    password: str


class BotConfig(BaseModel):
    token: str


class DatabaseConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str


class SessionConfig(BaseModel):
    key: str


class Config(BaseModel):
    admin: AdminConfig
    app: AppConfig
    bot: BotConfig
    database: DatabaseConfig
    session: SessionConfig


def setup_config(app: 'Application'):
    env_dict = dotenv.dotenv_values('.env')

    app.config = Config(
        app=AppConfig(debug=env_dict['DEBUG'] == 'true'),
        admin=AdminConfig(
            email=env_dict['ADMIN_EMAIL'],
            password=env_dict['ADMIN_PASS'],
        ),
        bot=BotConfig(
            token=env_dict['BOT_TOKEN'],
        ),
        database=DatabaseConfig(
            database=env_dict['PG_DB'],
            host=env_dict['PG_HOST'],
            port=int(env_dict['PG_PORT']),
            user=env_dict['PG_USER'],
            password=env_dict['PG_PASS'],
        ),
        session=SessionConfig(
            key=env_dict['SESSION_KEY'],
        ),
    )
