"""Application logging setup."""
import logging
import sys

from app.core.config import settings

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def setup_logging() -> None:
    level = logging.DEBUG if settings.APP_DEBUG else logging.INFO
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # Quiet noisy libs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING if not settings.APP_DEBUG else logging.INFO)
    # The OpenAI SDK (Yandex AI Studio client) dumps full request bodies at DEBUG — the
    # HTTP line from httpx at INFO ("POST https://ai.api.cloud.yandex.net/... 200") is enough.
    logging.getLogger("openai").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.INFO)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


logger = logging.getLogger(settings.APP_NAME)
