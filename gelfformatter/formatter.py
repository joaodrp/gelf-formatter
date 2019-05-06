"""Logging formatter for Graylog Extended Log Format (GELF).

This module implements a custom formatter for the Python standard library `logging`_
module that conforms to the `GELF Payload Specification Version 1.1`_.

.. _logging:
   https://docs.python.org/3/library/logging.html

.. _GELF Payload Specification Version 1.1:
   http://docs.graylog.org/en/3.0/pages/gelf.html#gelf-payload-specification
"""

import json
import logging
import socket

GELF_VERSION = "1.1"
"""str: GELF specification version."""

GELF_LEVELS = {
    logging.DEBUG: 7,
    logging.INFO: 6,
    logging.WARNING: 4,
    logging.ERROR: 3,
    logging.CRITICAL: 2,
}
"""dict: Map of logging levels vs syslog levels."""

GELF_IGNORED_ATTRS = ["id"]
"""List[str]: Attributes prohibited by the GELF specification."""

RESERVED_ATTRS = (
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
    "thread",
    "threadName",
)
"""List[str]: The `logging.LogRecord`_ attributes that should be ignored by default.

.. _logging.LogRecord:
   https://docs.python.org/3/library/logging.html#logrecord-attributes
"""


def _prefix(str):
    """Prefixes a string with an underscore.

    Args:
        str (str): The string to prefix.

    Returns:
        str: The prefixed string.
    """
    return str if str.startswith("_") else "_%s" % str


class GelfFormatter(logging.Formatter):
    """A custom logging formatter for GELF.

    This formatter extends the Python standard library `logging.Formatter`_ and conforms
    to the GELF specification.

    Attributes:
        reserved_fields: A dict of reserved `logging.LogRecord`_ attributes that will be
            included in all log messages.

        custom_fields: A dict of arbitrary custom additional attributes that will be
            included in all log messages.

    .. _logging.Formatter:
       https://docs.python.org/3/library/logging.html#logging.Formatter

    .. _logging.LogRecord:
       https://docs.python.org/3/library/logging.html#logrecord-attributes
    """

    def __init__(self, reserved_fields=None, custom_fields=None):
        """Initializes a GelfFormatter.

        Args:
            reserved_fields (Optional[dict]): A dict of reserved `logging.LogRecord`_
                attributes that should be included in all log messages (by default these
                attributes are excluded from the output). Keys should be the name of a
                `logging.LogRecord`_ attribute (listed in ``RESERVED_ATTRS`` and values
                should be the custom name to give to that additional attribute.
            custom_fields (Optional[dict]): A dict of arbitrary custom additional
                attributes that should be included in all log messages.

        .. _logging.LogRecord:
        https://docs.python.org/3/library/logging.html#logrecord-attributes
        """
        super(GelfFormatter, self).__init__()
        self.reserved_fields = reserved_fields
        self.custom_fields = custom_fields
        self._hostname = socket.gethostname()

    def format(self, record):
        """Formats a log record according to the GELF specification.

        Overrides `logging.Formatter.format`_.

        Args:
            record (logging.LogRecord): The original log record that should be converted
                and serialized to a GELF log message.

        Returns:
            str: The serialized GELF log message.

        .. _logging.Formatter.format:
           https://docs.python.org/3/library/logging.html#logging.Formatter.format
        """
        # Base GELF message structure
        log_record = dict(
            version=GELF_VERSION,
            short_message=record.getMessage(),
            timestamp=record.created,
            level=GELF_LEVELS[record.levelno],
            host=self._hostname,
        )

        # Capture exception info, if any
        if record.exc_info is not None:
            log_record["full_message"] = self.formatException(record.exc_info)

        record_dict = record.__dict__

        # Add `logging.LogRecord` additional fields, if any
        if self.reserved_fields:
            for key, value in self.reserved_fields.items():
                if key in record_dict:
                    log_record[_prefix(value)] = record_dict[key]

        # Add extra additional fields, if any
        if self.custom_fields:
            for key, value in self.custom_fields.items():
                if key not in GELF_IGNORED_ATTRS:
                    log_record[_prefix(key)] = value

        # Everything else is considered an additional attribute
        for key, value in record_dict.items():
            if key not in RESERVED_ATTRS and key not in GELF_IGNORED_ATTRS:
                log_record[_prefix(key)] = value

        # Serialize as JSON
        return json.dumps(log_record)
