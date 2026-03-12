import logging
import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_logging(app: 'Application') -> None:
    level = logging.DEBUG if app.config.app.debug else logging.INFO
    logging.basicConfig(level=level)
