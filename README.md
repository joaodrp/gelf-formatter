[![Release](https://img.shields.io/github/release/joaodrp/gelf-formatter.svg)](https://github.com/joaodrp/gelf-formatter/releases/latest)
[![PyPI](https://img.shields.io/pypi/v/gelf-formatter.svg)](https://pypi.org/project/gelf-formatter/)
[![Python versions](https://img.shields.io/pypi/pyversions/gelf-formatter.svg)](https://pypi.org/project/gelf-formatter/)
[![Travis](https://img.shields.io/travis/com/joaodrp/gelf-formatter.svg)](https://travis-ci.com/joaodrp/gelf-formatter)
[![Codecov](https://codecov.io/github/joaodrp/gelf-formatter/coverage.svg?branch=master)](https://codecov.io/github/joaodrp/gelf-formatter)
[![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](LICENSE)
[![SemVer](https://img.shields.io/badge/semver-2.0.0-blue.svg)](https://semver.org/)
[![Conventional Commits](https://img.shields.io/badge/conventional%20commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Downloads](https://pepy.tech/badge/gelf-formatter)](https://pepy.tech/project/gelf-formatter)
[![Contributors](https://img.shields.io/github/contributors/joaodrp/gelf-formatter.svg)](https://github.com/joaodrp/gelf-formatter/graphs/contributors)
[![SayThanks](https://img.shields.io/badge/say%20thanks-%E2%98%BC-1EAEDB.svg)](https://saythanks.io/to/joaodrp)

# GELF Formatter

[Graylog Extended Log Format (GELF)](http://docs.graylog.org/en/latest/pages/gelf.html) formatter for the Python standard library [logging](https://docs.python.org/3/library/logging.html) module.

## Motivation

There are several packages available providing *handlers* for the standard library logging module that can send your application logs to [Graylog](https://www.graylog.org/) by TCP/UDP/HTTP ([py-gelf](https://pypi.org/project/pygelf/) is a good example). Although these can be useful, it may not be a good idea to make your application performance dependent on costly network requests.

Alternatively, you can simply log to a file or `stdout` and have a collector (like [Fluentd](https://www.fluentd.org/)) processing and sending those logs *asynchronously* to a remote server (and not just to Graylog, as GELF can be used as a generic log format). This is a common pattern for containerized applications and in such scenarios all we need is a GELF logging *formatter*.

## Features

- Support for arbitrary additional fields (through `extra`);
- Support for including reserved [`logging.LogRecord`](https://docs.python.org/3/library/logging.html#logrecord-attributes) attributes as additional fields;
- Automatic detection and formatting of exceptions (traceback);
- Zero dependencies and tiny footprint.

## Installation

### With pip

```text
$ pip install gelf-formatter
```

### From source

```text
$ python setup.py install
```

## Usage

Simply create a `gelfformatter.GelfFormatter` instance and pass it as argument to [`logging.Handler.setFormatter`](https://docs.python.org/3/library/logging.html#logging.Handler.setFormatter):

```py
import sys
import logging

from gelfformatter import GelfFormatter

formatter = GelfFormatter()

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
```

Apply it globally with [`logging.basicConfig`](https://docs.python.org/3/library/logging.html#logging.basicConfig) to format log records from third-party packages as well:

```py
logging.basicConfig(level=logging.DEBUG, handlers=[handler])
```

Alternatively, you can configure a local [`logging.Logger`](https://docs.python.org/3/library/logging.html#logging.Logger) instance through [`logging.Logger.addHandler`](https://docs.python.org/3/library/logging.html#logging.Logger.addHandler).

That's it. You can now use the logging module as usual and all log records will be formatted as GELF messages.

### Standard Fields

The formatter will output all (non-deprecated) fields described in the [GELF Payload Specification (version 1.1)](http://docs.graylog.org/en/latest/pages/gelf.html#gelf-payload-specification):

- `version`: String, always set to `1.1`;

- `host`: String, the output of [`socket.gethostname`](https://docs.python.org/3/library/socket.html#socket.gethostname);
- `short_message`: String, log record message;
- `full_message` (*optional*): String, formatted traceback of an exception;
- `timestamp`: Number, millisecond precision epoch timestamp;
- `level`: Integer, *syslog* severity level corresponding to the Python logging level.

None of these fields can be ignored or override.

#### Example

```py
logging.info("Some message")
```

```text
{"version":"1.1","host":"my-server","short_message":"Some message","timestamp":1557342545.1067393,"level":6}
```

#### Exceptions

The `full_message` field is used to store the traceback of exceptions. You just need to log them with [`logging.exception`](https://docs.python.org/3/library/logging.html#logging.exception).

##### Example

```py
import urllib.request

req = urllib.request.Request('http://www.pythonnn.org')
try:
    urllib.request.urlopen(req)
except urllib.error.URLError as e:
    logging.exception(e.reason)
```

```text
{"version": "1.1", "short_message": "[Errno -2] Name or service not known", "timestamp": 1557342714.0695107, "level": 3, "host": "my-server", "full_message": "Traceback (most recent call last):\n  ...(truncated)... raise URLError(err)\nurllib.error.URLError: <urlopen error [Errno -2] Name or service not known>"}
```

### Additional Fields

The GELF specification allows any number of arbitrary additional fields, with keys prefixed with an underscore.

To log additional fields simply pass an object using the `extra` keyword. Keys will be automatically prefixed with an underscore (if not already).

#### Example

```py
logging.info("request received", extra={"path": "/orders/1", "method": "GET"})
```

```text
{"version": "1.1", "short_message": "request received", "timestamp": 1557343604.5892842, "level": 6, "host": "my-server", "_path": "/orders/1", "_method": "GET"}
```

#### Reserved Fields

By default the formatter ignores all [`logging.LogRecord` attributes](https://docs.python.org/3/library/logging.html#logrecord-attributes). You can however opt to have them automatically included as additional fields in all log messages. This can be used to display useful information like the current module, filename, line number, etc.

To do so, simply pass a `list` with the name of the the `LogRecord` attributes to include as value of the `allowed_reserved_attrs` keyword when initializing a `GelfFormatter` (or modify the corresponding instance variable directly). 

##### Example

```py
attrs = ["lineno", "module", "filename"]

formatter = GelfFormatter(allowed_reserved_attrs=attrs)
# or
formatter.allowed_reserved_attrs = attrs

logging.debug("starting application...")
```

```text
{"version": "1.1", "short_message": "starting application...", "timestamp": 1557346554.989846, "level": 6, "host": "my-server", "_lineno": 175, "_module": "myapp", "_filename": "app.py"}
```

You can optionally customize the name of these additional fields using a [`logging.Filter`](https://docs.python.org/3/library/logging.html#filter-objects) instead (see below for an example).

#### Context Fields

Having the ability to define a set of additional fields once and have them included as additional fields in all log messages can be useful to avoid repetitive `extra` key/value pairs and enable contextual logging.

Python's logging module provides several options to add context to a logger, among which we highlight the  [`logging.LoggerAdapter`](https://docs.python.org/3/library/logging.html#loggeradapter-objects) and [`logging.Filter`](https://docs.python.org/3/library/logging.html#filter-objects).

Between these we recommend the `logging.Filter`. Besides being simpler than a `LoggerAdapter`, it can be attached directly to a [`logging.Handler`](https://docs.python.org/3/library/logging.html#handler-objects), which makes it possible to use it for both custom logging instances and the global logging module (while a `LoggerAdapter` requires a logging instance to wrap).

You can also use `logging.Filter` to reuse any of the reserved `logging.LogRecord` attributes.

##### Example

```py
class ContextFilter(logging.Filter):
    def filter(self, record):
        # Add any number of arbitrary additional fields
        record.app = "my-app"
        record.app_version = "1.2.3"
        record.environment = os.environ.get("APP_ENV")
        
        # Reuse any reserved `logging.LogRecord` attributes
        record.file = record.filename
        record.line = record.lineno
        return True


formatter = GelfFormatter()
filter = ContextFilter()

handler = logging.StreamHandler(sys.stdout)

handler.setFormatter(formatter)
handler.addFilter(filter)

logging.basicConfig(level=logging.DEBUG, handlers=[handler])

logging.info("hi", extra=dict(foo="bar"))
```

```text
{"version": "1.1", "short_message": "hi", "timestamp": 1557431642.189755, "level": 6, "host": "my-server", "_foo": "bar", "_app": "my-app", "_app_version": "1.2.3", "_environment": "development", "_file": "formatter.py", "_line": 159}
```

#### 

## Pretty-Print

Looking for a GELF log pretty-printer? If so, have a look at [gelf-pretty](https://github.com/joaodrp/gelf-pretty).

## Contributions

This project adheres to the Contributor Covenant [code of conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please refer to our [contributing guide](CONTRIBUTING.md) for further information.






















