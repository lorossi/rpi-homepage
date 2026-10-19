"""Logging setup, based on loguru."""

import inspect
import logging
import sys

from loguru import logger

LOG_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} - {level} - {module} - "
    "{function} ({line}) - {message}"
)


class InterceptHandler(logging.Handler):
    """Forward records from the standard logging module to loguru.

    Used to capture the logs of third party libraries (uvicorn, apscheduler...).
    """

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record through loguru.

        Args:
            record (logging.LogRecord): The record to emit.
        """
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # find the caller from where the logged message originated
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def setup_logging(path: str = "server.log", level: str = "INFO") -> None:
    """Set up loguru sinks and route the standard logging module through it.

    Args:
        path (str, optional): The path of the log file. Defaults to "server.log".
        level (str, optional): The minimum log level. Defaults to "INFO".
    """
    logger.remove()
    logger.add(sys.stderr, level=level, format=LOG_FORMAT)
    logger.add(
        path,
        level=level,
        format=LOG_FORMAT,
        rotation="10 MB",
        retention=5,
        enqueue=True,
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
