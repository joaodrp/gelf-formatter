"""Logging formatter for Graylog Extended Log Format (GELF)"""

import logging
import socket
import traceback

from pythonjsonlogger.jsonlogger import RESERVED_ATTRS, JsonFormatter

# GELF specification version.
GELF_VERSION = "1.1"

# Map logging levels to syslog levels.
LEVELS = {
    logging.DEBUG: 7,
    logging.INFO: 6,
    logging.WARNING: 4,
    logging.ERROR: 3,
    logging.CRITICAL: 2,
}

# Attributes prohibited by the GELF specification.
IGNORED_ATTRS = ["id"]


def _prefix(str):
    return str if str.startswith("_") else "_%s" % str


class GelfFormatter(JsonFormatter):
    """
    A custom logging formatter for GELF.

    Extend `JsonFormatter`.
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

    def add_fields(self, log_record, record, message_dict):
        """
        Overrides `JsonFormatter.add_fields` to transform log records according to the
        GELF 1.1 specification.

        :param log_record: The output log record
        :type log_record: OrderedDict :param
        record: The input log record
        :type record: logging.LogRecord
        :param message_dict: Additional fields (not used, ignore)
        :type message_dict: dict

        .. seealso::
            http://docs.graylog.org/en/3.0/pages/gelf.html#gelf-payload-specification
        """

        # Base GELF message structure
        log_record.update(
            version=GELF_VERSION,
            short_message=record.getMessage(),
            timestamp=record.created,
            level=LEVELS[record.levelno],
            host=self.hostname,
        )

        # Capture exception info, if any
        if record.exc_info is not None:
            log_record["full_message"] = "\n".join(
                traceback.format_exception(*record.exc_info)
            )

        record_dict = record.__dict__

        # Add `logging.LogRecord` additional fields, if any
        if self.logrecord_add_fields:
            for key, value in self.logrecord_add_fields.items():
                if key in record_dict:
                    log_record[_prefix(value)] = record_dict[key]

        # Add extra additional fields, if any
        if self.extra_add_fields:
            for key, value in self.extra_add_fields.items():
                if key not in IGNORED_ATTRS:
                    log_record[_prefix(key)] = value

        # Everything else is considered an additional attribute
        for key, value in record_dict.items():
            if key not in RESERVED_ATTRS and key not in IGNORED_ATTRS:
                log_record[_prefix(key)] = value
