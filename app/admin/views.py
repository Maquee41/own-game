from aiohttp_apispec import docs, request_schema, response_schema

from app.admin.schemes import AdminSchema
from app.web.app import View


# TODO
# Write admin login view
class AdminLoginView(View):
    @docs(tags=["admin"])
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        raise NotImplementedError


# TODO
# Write admin "me" route
class AdminCurrentView(View):
    @docs(tags=["admin"])
    @response_schema(AdminSchema, 200)
    async def get(self):
        raise NotImplementedError
