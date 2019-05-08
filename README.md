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

- Support for custom additional fields (context);
- Support for reserved [`logging.LogRecord`](https://docs.python.org/3/library/logging.html#logrecord-attributes) additional fields;
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

#### Fixed Fields (Context)

It's possible to tell the formatter to included a predefined set of additional fields in all log messages. This is useful for repetitive additional fields and facilitates contextual logging.

To do so, simply pass a `dict` of fixed additional fields as `custom_fields` when initializing a `GelfFormatter`, or modify the `custom_fields` instance variable directly.

##### Example

```py
fields = {"app": "my-app", "version": "1.0.1"}

formatter = GelfFormatter(custom_fields=fields)
# or
formatter.custom_fields = fields

logging.debug("starting application...")
```

```text
{"version": "1.1", "short_message": "starting application...", "timestamp": 1557344270.2869651, "level": 6, "host": "my-server", "_app": "my-app", "_version": "1.0.1"}
```

#### Reserved Fields

It's possible to include any of the [`logging.LogRecord` attributes](https://docs.python.org/3/library/logging.html#logrecord-attributes) as additional fields in all log messages. This can be used to include useful information like the current module and filename, line number, etc.

To do so, simply pass a `dict` as `reserved_fields` when initializing a `GelfFormatter`, or modify the `reserved_fields` instance variable directly. Keys must be the name of a `LogRecord` attribute and values must be the name to use for that additional field.

##### Example

```py
fields = {"lineno": "line", "module": "module", "filename": "file"}

formatter = GelfFormatter(reserved_fields=fields)
# or
formatter.reserved_fields = fields

logging.debug("starting application...")
```

```text
{"version": "1.1", "short_message": "starting application...", "timestamp": 1557346554.989846, "level": 6, "host": "my-server", "_line": 175, "_module": "myapp", "_file": "app.py"}
```


## Pretty-Print

Looking for a GELF log pretty-printer? If so, have a look at [gelf-pretty](https://github.com/joaodrp/gelf-pretty).

## Contributions

This project adheres to the Contributor Covenant [code of conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please refer to our [contributing guide](CONTRIBUTING.md) for further information.






















