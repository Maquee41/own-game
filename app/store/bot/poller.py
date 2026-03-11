import asyncio
from asyncio import Future, Task

from app.store import Store


class Poller:
    def __init__(self, store: Store) -> None:
        self.store = store
        self.is_running = False
        self.poll_task: Task | None = None

    def _done_callback(self, result: Future) -> None:
        try:
            exc = result.exception()
        except asyncio.CancelledError:
            return

        if exc:
            self.store.app.logger.exception(
                'poller stopped with exception', exc_info=exc
            )

        if self.is_running and exc:
            self.start()

    def start(self) -> None:
        if self.is_running:
            return

        self.is_running = True
        self.poll_task = asyncio.create_task(self.poll())
        self.poll_task.add_done_callback(self._done_callback)

    async def stop(self) -> None:
        self.is_running = False

        if self.poll_task:
            self.poll_task.cancel()
            try:
                await self.poll_task
            except asyncio.CancelledError:
                ...

    async def poll(self) -> None:
        while self.is_running:
            try:
                await self.store.bot.manager.poll()
            except asyncio.CancelledError:
                raise
            except Exception:
                self.store.app.logger.exception('poll iteration failed')
                await asyncio.sleep(1)
