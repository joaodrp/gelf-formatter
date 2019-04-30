import json
import logging
import traceback
from io import StringIO
from unittest import TestCase, mock

from gelfformatter.formatter import LEVELS, GelfFormatter

TIME = 1556565019.768748
HOST = "server-x"
MSG = "test message"
REPEATED = {"version": "1.1", "short_message": MSG, "timestamp": TIME, "host": HOST}


@mock.patch("time.time", mock.MagicMock(return_value=TIME))
@mock.patch("socket.gethostname", mock.MagicMock(return_value=HOST))
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
        self.assertEqual(gelf, {**REPEATED, "level": 6})

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
                **REPEATED,
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
        full_message = traceback.format_exc()

        self.logger.exception(MSG)

        gelf = json.loads(self.buffer.getvalue())
        self.assertEqual(gelf, {**REPEATED, "level": 3, "full_message": full_message})

    def testLevels(self):
        formatter = GelfFormatter()
        self.log_handler.setFormatter(formatter)

        for logging_level, syslog_level in LEVELS.items():
            self.logger.log(logging_level, MSG)
            gelf = json.loads(self.buffer.getvalue())
            self.assertEqual(gelf, {**REPEATED, "level": syslog_level})
            self.buffer.truncate(0)
            self.buffer.seek(0)

    def testLogRecordAddFields(self):
        formatter = GelfFormatter(
            logrecord_add_fields={
                "filename": "file",
                "funcName": "func_name",
                "levelname": "level_name",
                "module": "module",
                "name": "name",
                "does_not_exists": "foo",
            }
        )
        self.log_handler.setFormatter(formatter)

        self.logger.info(MSG)

        gelf = json.loads(self.buffer.getvalue())
        self.assertEqual(
            gelf,
            {
                **REPEATED,
                "level": 6,
                "_file": "test_formatter.py",
                "_func_name": "testLogRecordAddFields",
                "_level_name": "INFO",
                "_module": "test_formatter",
                "_name": "test",
            },
        )

    def testExtraAddFields(self):
        formatter = GelfFormatter(
            extra_add_fields={
                "app": "my-app",
                "environment": "development",
                "id": "this should be ignored",
            }
        )
        self.log_handler.setFormatter(formatter)

        self.logger.info(MSG)

        gelf = json.loads(self.buffer.getvalue())
        self.assertEqual(
            gelf,
            {**REPEATED, "level": 6, "_app": "my-app", "_environment": "development"},
        )
