from app.aiotg.types.user import User


async def get_me(bot) -> User:
    return await bot.request('getMe', response_model=User)
