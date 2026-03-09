from typing import TYPE_CHECKING

from app.admin.models import AdminModel
from app.base.base_accessor import BaseAccessor

if TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: 'Application') -> None:
        await self.app.database.connect()

    async def get_by_email(self, email: str) -> AdminModel | None:
        raise NotImplementedError

    async def create_admin(self, email: str, password: str) -> AdminModel:
        raise NotImplementedError
