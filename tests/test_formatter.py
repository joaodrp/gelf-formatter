import json
import logging
import traceback
from unittest import TestCase

from mock import MagicMock, patch  # Python 2.7 support

from gelfformatter.formatter import GELF_LEVELS, GelfFormatter, _prefix

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO  # Python 3 support


TIME = 1556565019.768748
HOST = "server-x"
MSG = "test message"


def chomp(x):
    if x.endswith("\r\n"):
        return x[:-2]
    if x.endswith("\n") or x.endswith("\r"):
        return x[:-1]
    return x


@patch("time.time", MagicMock(return_value=TIME))
@patch("socket.gethostname", MagicMock(return_value=HOST))
class TestGelfFormatter(TestCase):
    def setUp(self):
        self.logger = logging.getLogger("test")
        self.logger.setLevel(logging.DEBUG)

        self.buffer = StringIO()
        self.log_handler = logging.StreamHandler(self.buffer)

        self.logger.addHandler(self.log_handler)

    def testBase(self):
        formatter = GelfFormatter()
        self.log_handler.setFormatter(formatter)

        self.logger.info(MSG)

        gelf = json.loads(self.buffer.getvalue())
        self.assertEqual(
            gelf,
            {
                "version": "1.1",
                "short_message": MSG,
                "timestamp": TIME,
                "host": HOST,
                "level": 6,
            },
        )

    def testExtra(self):
        formatter = GelfFormatter()
        self.log_handler.setFormatter(formatter)

        extra = {
            "string": "bar",
            "int": 1,
            "float": 1.2,
            "bool": True,
            "array": [1, 2, 3],
            "object": {"a": "b"},
        }
        self.logger.info(MSG, extra=extra)

        gelf = json.loads(self.buffer.getvalue())
        self.assertEqual(
            gelf,
            {
                "version": "1.1",
                "short_message": MSG,
                "timestamp": TIME,
                "host": HOST,
                "level": 6,
                "_string": extra["string"],
                "_int": extra["int"],
                "_float": extra["float"],
                "_bool": extra["bool"],
                "_array": extra["array"],
                "_object": extra["object"],
            },
        )

    def testExcInfo(self):
        formatter = GelfFormatter()
        self.log_handler.setFormatter(formatter)

        try:
            raise Exception("some error")
        except Exception:
            pass

        full_message = chomp(traceback.format_exc())

        self.logger.exception(MSG)

        gelf = json.loads(self.buffer.getvalue())
        self.assertEqual(gelf["full_message"], full_message)

    def testLevels(self):
        formatter = GelfFormatter()
        self.log_handler.setFormatter(formatter)

        for logging_level, syslog_level in GELF_LEVELS.items():
            self.logger.log(logging_level, MSG)
            gelf = json.loads(self.buffer.getvalue())
            self.assertEqual(
                gelf,
                {
                    "version": "1.1",
                    "short_message": MSG,
                    "timestamp": TIME,
                    "host": HOST,
                    "level": syslog_level,
                },
            )
            self.buffer.truncate(0)
            self.buffer.seek(0)

    def testLogRecordAddFields(self):
        formatter = GelfFormatter(
            allowed_reserved_attrs=["module", "filename", "this should be ignored"]
        )
        self.log_handler.setFormatter(formatter)

        self.logger.info(MSG)

        gelf = json.loads(self.buffer.getvalue())
        self.assertEqual(
            gelf,
            {
                "version": "1.1",
                "short_message": MSG,
                "timestamp": TIME,
                "host": HOST,
                "level": 6,
                "_filename": "test_formatter.py",
                "_module": "test_formatter",
            },
        )


class TestUtilityMethods(TestCase):
    def testUnderscorePrefix(self):
        self.assertEqual(_prefix("foo"), "_foo")
        self.assertEqual(_prefix("_foo"), "_foo")
