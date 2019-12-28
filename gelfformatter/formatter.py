"""Logging formatter for Graylog Extended Log Format (GELF).

This module implements a custom formatter for the Python standard library `logging`_
module that conforms to the `GELF Payload Specification Version 1.1`_.

.. _logging:
   https://docs.python.org/3/library/logging.html

.. _GELF Payload Specification Version 1.1:
   http://docs.graylog.org/en/3.0/pages/gelf.html#gelf-payload-specification
"""

import itertools
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

    def __init__(self, allowed_reserved_attrs=[], ignored_attrs=[]):
        """Initializes a GelfFormatter."""
        super(GelfFormatter, self).__init__()
        self.allowed_reserved_attrs = allowed_reserved_attrs
        self.ignored_attrs = ignored_attrs
        self._hostname = socket.gethostname()

    def prepare_basic(self, record):
        """Prepares the basics necessary for a log record.

        Args:
            record (logging.LogRecord): The original log record that should be formatted
                as a GELF log message.

        Returns:
            dict: A basic log record.
        """
        # Set asctime field if required
        if "asctime" in self.allowed_reserved_attrs:
            record.asctime = self.formatTime(record)

        # Base GELF message structure
        log_record = dict(
            version=GELF_VERSION,
            short_message=record.getMessage(),
            timestamp=record.created,
            level=GELF_LEVELS[record.levelno],
            host=self._hostname,
        )

        # Capture exception info, if any
        if record.exc_info:
            log_record["full_message"] = self.formatException(record.exc_info)

        return log_record

    def filter(self, key, value, excluded_attrs):
        """Optional log fields may be modified/removed.

        Args:
            key (str): The log field key.
            value: The log fields value.
            excluded_attrs (list): Values to filter out.

        Returns:
            tuple: A tuple containing the modified fields.
        """
        if key not in itertools.chain(GELF_IGNORED_ATTRS, excluded_attrs):
            if isinstance(value, dict):
                filtered = dict()
                for k, v in value.items():
                    k, v = self.filter(k, v, excluded_attrs)
                    if k:
                        filtered[k] = v
                return key, filtered
            return key, value
        return (None, None)

    def get_optionals(self, record):
        """Adds optional log fields from the original record.

        Args:
            record (logging.LogRecord): The original log record with
            optional fields set.

        Returns:
            dict: The optional fields with gelf compliant naming.
        """

        optionals = dict()

        # Compute excluded attributes
        excluded_attrs = [
            x for x in RESERVED_ATTRS if x not in self.allowed_reserved_attrs
        ]
        excluded_attrs += self.ignored_attrs

        for key, value in record.__dict__.items():
            key, value = self.filter(key, value, excluded_attrs)
            if key:
                optionals[_prefix(key)] = value

        return optionals

    def format(self, record):
        """Formats a log record according to the GELF specification.

        Overrides `logging.Formatter.format`_.
        First computes the required fields for a gelf message,
        then adds optional fields.

        Args:
            record (logging.LogRecord): The original log record that should be formatted
                as a GELF log message.

        Returns:
            str: The serialized JSON GELF log message.

        .. _logging.Formatter.format:
           https://docs.python.org/3/library/logging.html#logging.Formatter.format
        """

        gelf_record = self.prepare_basic(record)
        gelf_record.update(self.get_optionals(record))

        # Serialize as JSON
        return json.dumps(gelf_record)
