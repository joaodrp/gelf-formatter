"""
GELF logging formatter module.
"""
import logging
import socket
import traceback

from pythonjsonlogger.jsonlogger import RESERVED_ATTRS, JsonFormatter

GELF_VERSION = "1.1"

LEVELS = {
    logging.DEBUG: 7,
    logging.INFO: 6,
    logging.WARNING: 4,
    logging.ERROR: 3,
    logging.CRITICAL: 2,
}

IGNORED_ATTRS = ["id"]


def _prefix(str):
    return str if str.startswith("_") else "_%s" % str


class GelfFormatter(JsonFormatter):
    def __init__(self, logrecord_add_fields=None, extra_add_fields=None):
        super(GelfFormatter, self).__init__()
        self.logrecord_add_fields = logrecord_add_fields
        self.extra_add_fields = extra_add_fields
        self.hostname = socket.gethostname()

    def add_fields(self, log_record, record, message):
        log_record.update(
            version=GELF_VERSION,
            short_message=record.getMessage(),
            timestamp=record.created,
            level=LEVELS[record.levelno],
            host=self.hostname,
        )

        if record.exc_info is not None:
            log_record["full_message"] = "\n".join(
                traceback.format_exception(*record.exc_info)
            )

        record_dict = record.__dict__

        if self.logrecord_add_fields:
            for key, value in self.logrecord_add_fields.items():
                if key in record_dict:
                    log_record[_prefix(value)] = record_dict[key]

        if self.extra_add_fields:
            for key, value in self.extra_add_fields.items():
                if key not in IGNORED_ATTRS:
                    log_record[_prefix(key)] = value

        for key, value in record_dict.items():
            if key not in RESERVED_ATTRS and key not in IGNORED_ATTRS:
                log_record[_prefix(key)] = value
