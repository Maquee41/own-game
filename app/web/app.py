from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
    View as AiohttpView,
)
from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas import setup as setup_pydantic_apispec
from aiohttp_session import setup as session_setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from app.admin.models import AdminModel
from app.store import Store, setup_store
from app.store.database.database import Database
from app.web.config import Config, setup_config
from app.web.logger import setup_logging
from app.web.middlewares import setup_middlewares
from app.web.routes import setup_routes


class Application(AiohttpApplication):
    config: Config | None = None
    store: Store
    database: Database


class Request(AiohttpRequest):
    admin: AdminModel | None = None

    @property
    def app(self) -> Application:
        return super().app()


class View(PydanticView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def database(self) -> Database:
        return self.request.app.database

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})


app = Application()


def setup_app() -> Application:
    setup_logging(app)
    setup_config(app)
    session_setup(app, EncryptedCookieStorage(app.config.session.key))
    setup_routes(app)
    setup_pydantic_apispec(app, title_spec="Own Game Bot", url_prefix="/docs")
    setup_middlewares(app)
    setup_store(app)
    return app
