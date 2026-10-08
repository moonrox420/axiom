from .core.config import settings
from .core.logging import setup_logging

setup_logging()

__all__ = ["settings"]
