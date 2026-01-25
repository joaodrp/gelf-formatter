"""Logging formatter for Graylog Extended Log Format (GELF).

This module implements a custom formatter for the Python standard library `logging`_
module that conforms to the `GELF Payload Specification Version 1.1`_.

.. _logging:
   https://docs.python.org/3/library/logging.html

.. _GELF Payload Specification Version 1.1:
   http://docs.graylog.org/en/3.0/pages/gelf.html#gelf-payload-specification
"""

from __future__ import annotations

import json
import logging
import socket
from typing import Any

GELF_VERSION: str = "1.1"
"""GELF specification version."""

GELF_LEVELS: dict[int, int] = {
    logging.DEBUG: 7,
    logging.INFO: 6,
    logging.WARNING: 4,
    logging.ERROR: 3,
    logging.CRITICAL: 2,
}
"""Map of logging levels vs syslog levels."""

GELF_IGNORED_ATTRS: list[str] = ["id"]
"""Attributes prohibited by the GELF specification."""

RESERVED_ATTRS: tuple[str, ...] = (
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "taskName",
    "thread",
    "threadName",
)
"""The `logging.LogRecord`_ attributes that should be ignored by default.

.. _logging.LogRecord:
   https://docs.python.org/3/library/logging.html#logrecord-attributes
"""


def _prefix(value: str) -> str:
    """Prefixes a string with an underscore.

    Args:
        value: The string to prefix.

    Returns:
        The prefixed string.
    """
    return value if value.startswith("_") else f"_{value}"


class GelfFormatter(logging.Formatter):
    """A custom logging formatter for GELF.

    This formatter extends the Python standard library `logging.Formatter`_ and conforms
    to the GELF specification.

    Attributes:
        allowed_reserved_attrs: A list of reserved `logging.LogRecord`_ attributes that
        should not be ignored but rather included as additional fields.

        ignored_attrs: A list of additional attributes passed to a `logging.LogRecord`_
        via the `extra` keyword that will be ignored in addition to the reserved fields
        and not be present in the ouput.

    .. _logging.Formatter:
       https://docs.python.org/3/library/logging.html#logging.Formatter

    .. _logging.LogRecord:
       https://docs.python.org/3/library/logging.html#logrecord-attributes
    """

    allowed_reserved_attrs: list[str]
    ignored_attrs: list[str]
    _hostname: str

    def __init__(
        self,
        allowed_reserved_attrs: list[str] | None = None,
        ignored_attrs: list[str] | None = None,
    ) -> None:
        """Initializes a GelfFormatter."""
        super().__init__()
        self.allowed_reserved_attrs = allowed_reserved_attrs or []
        self.ignored_attrs = ignored_attrs or []
        self._hostname = socket.gethostname()

    def format(self, record: logging.LogRecord) -> str:
        """Formats a log record according to the GELF specification.

        Overrides `logging.Formatter.format`_.

        Args:
            record: The original log record that should be formatted
                as a GELF log message.

        Returns:
            The serialized JSON GELF log message.

        .. _logging.Formatter.format:
           https://docs.python.org/3/library/logging.html#logging.Formatter.format
        """
        # Base GELF message structure
        log_record: dict[str, Any] = {
            "version": GELF_VERSION,
            "short_message": record.getMessage(),
            "timestamp": record.created,
            "level": GELF_LEVELS[record.levelno],
            "host": self._hostname,
        }

        # Capture exception info, if any
        if record.exc_info is not None:
            log_record["full_message"] = self.formatException(record.exc_info)

        # Set asctime field if required
        if "asctime" in self.allowed_reserved_attrs:
            record.asctime = self.formatTime(record)

        # Compute excluded attributes
        excluded_attrs: list[str] = [
            x for x in RESERVED_ATTRS if x not in self.allowed_reserved_attrs
        ]
        excluded_attrs += self.ignored_attrs

        # Everything else is considered an additional attribute
        for key, value in record.__dict__.items():
            if key not in GELF_IGNORED_ATTRS and key not in excluded_attrs:
                try:
                    json.dumps(value)
                except (TypeError, OverflowError):
                    # If value is not JSON serializable, convert to string
                    log_record[_prefix(key)] = str(value)
                else:
                    # If value is JSON serializable,
                    # value will be encoded in the following return
                    log_record[_prefix(key)] = value

        # Serialize as JSON
        return json.dumps(log_record)
