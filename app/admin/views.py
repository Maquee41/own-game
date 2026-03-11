from aiohttp_pydantic.oas.typing import r200

from app.admin.schemas import AdminSchema
from app.web.app import View


# TODO
# Write admin login view
class AdminLoginView(View):
    async def post(self, admin: AdminSchema) -> r200[AdminSchema]:
        """
        Login admin

        Tags: admin
        """
        raise NotImplementedError


# TODO
# Write admin "me" route
class AdminCurrentView(View):
    async def get(self) -> r200[AdminSchema]:
        """
        Get yourself

        Tags: admin
        """
        raise NotImplementedError
