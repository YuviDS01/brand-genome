"""
Basic logging setup. Format intentionally mirrors the bracketed-tag style
from Section 43 of the architecture doc, e.g. "[JOB] Created research job 123",
so log lines stay greppable by layer once the worker/crawler/processor start
emitting them in later steps.
"""

import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]

    # Quiet down noisy third-party loggers at INFO; keep our own app.* verbose.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
