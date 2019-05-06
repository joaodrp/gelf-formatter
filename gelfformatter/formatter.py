"""Logging formatter for Graylog Extended Log Format (GELF)"""

import json
import logging
import socket

# GELF specification version.
GELF_VERSION = "1.1"

# Map logging levels to syslog levels.
GELF_LEVELS = {
    logging.DEBUG: 7,
    logging.INFO: 6,
    logging.WARNING: 4,
    logging.ERROR: 3,
    logging.CRITICAL: 2,
}

# Attributes prohibited by the GELF specification.
GELF_IGNORED_ATTRS = ["id"]


# The `logging.LogRecord` attributes that should be ignored by default.
# http://docs.python.org/library/logging.html#logrecord-attributes
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


def _prefix(str):
    return str if str.startswith("_") else "_%s" % str


class GelfFormatter(logging.Formatter):
    """
    A custom logging formatter for GELF.

    .. seealso::
    https://docs.python.org/3/library/logging.html#logging.Formatter
    http://docs.graylog.org/en/3.0/pages/gelf.html#gelf-payload-specification
    """

    def __init__(self, logrecord_add_fields=None, extra_add_fields=None):
        """
        :param logrecord_add_fields: Additional `logging.LogRecord` attributes that
            should be included in all log messages. Keys should be the name of a
            `LogRecord` attribute and values should be the custom name to give to that
            additional attribute in the GELF log message (default is None)
        :type logrecord_add_fields: dict
        :param extra_add_fields: Arbitrary additional attributes that should be included
            in all log messages (default is None)
        :type extra_add_fields: dict

        .. seealso:: http://docs.python.org/library/logging.html#logrecord-attributes
        """
        super(GelfFormatter, self).__init__()
        self.logrecord_add_fields = logrecord_add_fields
        self.extra_add_fields = extra_add_fields
        self.hostname = socket.gethostname()

    def format(self, record):
        """Formats a log record according to the GELF specification.

        :param record: The original log record
        :type record: logging.LogRecord

        .. seealso::
        https://docs.python.org/3/library/logging.html#logging.Formatter.format
        """
        # Base GELF message structure
        log_record = dict(
            version=GELF_VERSION,
            short_message=record.getMessage(),
            timestamp=record.created,
            level=GELF_LEVELS[record.levelno],
            host=self.hostname,
        )

        # Capture exception info, if any
        if record.exc_info is not None:
            log_record["full_message"] = self.formatException(record.exc_info)

        record_dict = record.__dict__

        # Add `logging.LogRecord` additional fields, if any
        if self.logrecord_add_fields:
            for key, value in self.logrecord_add_fields.items():
                if key in record_dict:
                    log_record[_prefix(value)] = record_dict[key]

        # Add extra additional fields, if any
        if self.extra_add_fields:
            for key, value in self.extra_add_fields.items():
                if key not in GELF_IGNORED_ATTRS:
                    log_record[_prefix(key)] = value

        # Everything else is considered an additional attribute
        for key, value in record_dict.items():
            if key not in RESERVED_ATTRS and key not in GELF_IGNORED_ATTRS:
                log_record[_prefix(key)] = value

        return json.dumps(log_record)
