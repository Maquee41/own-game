async def answer_callback_query(
    bot,
    callback_query_id: str,
    text: str | None = None,
    show_alert: bool = False,
) -> bool:
    data = {
        'callback_query_id': callback_query_id,
        'show_alert': show_alert,
    }
    if text is not None:
        data['text'] = text

    result = await bot.request('answerCallbackQuery', data=data)
    return bool(result)
