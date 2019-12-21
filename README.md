<h1 align="center" style="border-bottom: none;">GELF Formatter</h1>
<h3 align="center">
    <a href="http://docs.graylog.org/en/latest/pages/gelf.html">Graylog Extended Log Format (GELF)</a> formatter for the<br>Python standard library <a href="https://docs.python.org/3/library/logging.html">logging</a> module
</h3>
<p align="center">
    <a href="https://github.com/joaodrp/gelf-formatter/releases/latest">
        <img alt="Release" src="https://img.shields.io/github/release/joaodrp/gelf-formatter.svg">
    </a>
    <a href="https://pypi.org/project/gelf-formatter/">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/gelf-formatter.svg">
    </a>
    <a href="https://pypi.org/project/gelf-formatter/">
        <img alt="Python versions" src="https://img.shields.io/pypi/pyversions/gelf-formatter.svg">
    </a>
    <a href="https://travis-ci.com/joaodrp/gelf-formatter">
        <img alt="Travis" src="https://img.shields.io/travis/com/joaodrp/gelf-formatter.svg">
    </a>
    <a href="https://codecov.io/gh/joaodrp/gelf-formatter">
        <img alt="Codecov" src="https://img.shields.io/codecov/c/github/joaodrp/gelf-formatter/master.svg">
    </a>
    <a href="LICENSE">
        <img alt="Software License" src="https://img.shields.io/badge/license-MIT-brightgreen.svg">
    </a>
    <a href="https://semver.org/">
        <img alt="SemVer" src="https://img.shields.io/badge/semver-2.0.0-blue.svg">
    </a>
    <a href="https://conventionalcommits.org">
        <img alt="Conventional Commits" src="https://img.shields.io/badge/conventional%20commits-1.0.0-yellow.svg">
    </a>
    <a href="https://github.com/ambv/black">
        <img alt="Code style" src="https://img.shields.io/badge/code%20style-black-000000.svg">
    </a>
    <a href="https://pepy.tech/project/gelf-formatter">
        <img alt="Downloads" src="https://pepy.tech/badge/gelf-formatter">
    </a>
    <a href="https://github.com/joaodrp/gelf-formatter/graphs/contributors">
        <img alt="Contributors" src="https://img.shields.io/github/contributors/joaodrp/gelf-formatter.svg">
    </a>
    <a href="https://saythanks.io/to/joaodrp">
        <img alt="SayThanks.io" src="https://img.shields.io/badge/say%20thanks-%E2%98%BC-1EAEDB.svg">
    </a>
</p>

---

## Motivation

There are several packages available providing *handlers* for the standard library logging module that can send application logs to [Graylog](https://www.graylog.org/) by TCP/UDP/HTTP ([py-gelf](https://pypi.org/project/pygelf/) is a good example). Although these can be useful, it's not ideal to make an application performance dependent on network requests just for the purpose of delivering logs.

Alternatively, one can simply log to a file or `stdout` and have a collector (like [Fluentd](https://www.fluentd.org/)) processing and sending those logs *asynchronously* to a remote server (and not just to Graylog, as GELF can be used as a generic log format), which is a common pattern for containerized applications. In a scenario like this all we need is a GELF logging *formatter*.

## Features

- Support for arbitrary additional fields;
- Support for including reserved [`logging.LogRecord`](https://docs.python.org/3/library/logging.html#logrecord-attributes) attributes as additional fields;
- Exceptions detection with traceback formatting;
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

```python
import sys
import logging

from gelfformatter import GelfFormatter

formatter = GelfFormatter()

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
```

Apply it globally with [`logging.basicConfig`](https://docs.python.org/3/library/logging.html#logging.basicConfig) to automatically format log records from third-party packages as well:

```python
logging.basicConfig(level=logging.DEBUG, handlers=[handler])
```

Alternatively, you can configure a local [`logging.Logger`](https://docs.python.org/3/library/logging.html#logging.Logger) instance through [`logging.Logger.addHandler`](https://docs.python.org/3/library/logging.html#logging.Logger.addHandler):

```python
logger = logging.getLogger('my-app')
logger.addHandler(handler)
```

That's it. You can now use the logging module as usual, all records will be formatted as GELF messages.

### Standard Fields

The formatter will output all (non-deprecated) fields described in the [GELF Payload Specification (version 1.1)](http://docs.graylog.org/en/latest/pages/gelf.html#gelf-payload-specification):

- `version`: String, always set to `1.1`;

- `host`: String, the output of [`socket.gethostname`](https://docs.python.org/3/library/socket.html#socket.gethostname) at initialization;
- `short_message`: String, log record message;
- `full_message` (*optional*): String, formatted exception traceback (if any);
- `timestamp`: Number, time in seconds since the epoch as a floating point;
- `level`: Integer, *syslog* severity level.

None of these fields can be ignored, renamed or overridden.

#### Example

```python
logging.info("Some message")
```

```text
{"version":"1.1","host":"my-server","short_message":"Some message","timestamp":1557342545.1067393,"level":6}
```

#### Exceptions

The `full_message` field is used to store the traceback of exceptions. You just need to log them with [`logging.exception`](https://docs.python.org/3/library/logging.html#logging.exception).

##### Example

```python
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

The GELF specification allows arbitrary additional fields, with keys prefixed with an underscore.

To include additional fields use the standard logging `extra` keyword. Keys will be automatically prefixed with an underscore (if not already).

#### Example

```python
logging.info("request received", extra={"path": "/orders/1", "method": "GET"})
```

```text
{"version": "1.1", "short_message": "request received", "timestamp": 1557343604.5892842, "level": 6, "host": "my-server", "_path": "/orders/1", "_method": "GET"}
```

#### Reserved Fields

By default the formatter ignores all [`logging.LogRecord` attributes](https://docs.python.org/3/library/logging.html#logrecord-attributes). You can however opt to include them as additional fields. This can be used to display useful information like the current module, filename, line number, etc.

To do so, simply pass a list of `LogRecord` attribute names as value of the `allowed_reserved_attrs` keyword when initializing a `GelfFormatter`. You can also modify the `allowed_reserved_attrs` instance variable of an already initialized formatter.

##### Example

```python
attrs = ["lineno", "module", "filename"]

formatter = GelfFormatter(allowed_reserved_attrs=attrs)
# or
formatter.allowed_reserved_attrs = attrs

logging.debug("starting application...")
```

```text
{"version": "1.1", "short_message": "starting application...", "timestamp": 1557346554.989846, "level": 6, "host": "my-server", "_lineno": 175, "_module": "myapp", "_filename": "app.py"}
```

You can optionally customize the name of these additional fields using a [`logging.Filter`](https://docs.python.org/3/library/logging.html#filter-objects) (see below).

Similarily, you can choose to ignore additional attributes passed via the `extra` keyword argument. This can be usefull to e.g. not log keywords named `secret` or `password`.

To do so, pass a list of names to the `ignored_attrs` keyword when initializing a `GelfFormatter`. You can also modify the `ignored_attrs` instance variable of an already initialized formatter.

##### Example

But be aware: nested fields will be printed! Only the root level of keywords is filtered by the `ignored_attrs`.

```python
attrs = ["secret", "password"]

formatter = GelfFormatter(ignored_attrs=attrs)
# or
formatter.ignored_attrs = attrs

logging.debug("app config", extra={"connection": "local", "secret": "verySecret!", "mysql": {"user": "test", "password": "will_be_logged"}})
```

```text
{"version": "1.1", "short_message": "app config", "timestamp": 1557346554.989846, "level": 6, "host": "my-server", "_connection": "local", "_mysql": {"user": "test", "password": "will_be_logged"}}
```


#### Context Fields

Having the ability to define a set of additional fields once and have them included in all log messages can be useful to avoid repetitive `extra` key/value pairs and enable contextual logging.

Python's logging module provides several options to add context to a logger, among which we highlight the  [`logging.LoggerAdapter`](https://docs.python.org/3/library/logging.html#loggeradapter-objects) and [`logging.Filter`](https://docs.python.org/3/library/logging.html#filter-objects).

Between these we recommend a `logging.Filter`, which is simpler and can be attached directly to a [`logging.Handler`](https://docs.python.org/3/library/logging.html#handler-objects). A `logging.Filter` can therefore be used locally (on a [`logging.Logger`](https://docs.python.org/3/library/logging.html#logger-objects)) or globally (through `logging.basicConfig`). If you opt for a `LoggerAdapter` you'll need a `logging.Logger` to wrap.

You can also use a `logging.Filter` to reuse/rename any of the reserved `logging.LogRecord` attributes.

##### Example

```python
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

handler = logging.StreamHandler(sys.stdout)

handler.setFormatter(formatter)
handler.addFilter(ContextFilter())

logging.basicConfig(level=logging.DEBUG, handlers=[handler])

logging.info("hi", extra=dict(foo="bar"))
```

```text
{"version": "1.1", "short_message": "hi", "timestamp": 1557431642.189755, "level": 6, "host": "my-server", "_foo": "bar", "_app": "my-app", "_app_version": "1.2.3", "_environment": "development", "_file": "app.py", "_line": 159}
```

## Pretty-Print

Looking for a GELF log pretty-printer? If so, have a look at [gelf-pretty](https://github.com/joaodrp/gelf-pretty) :fire:

## Contributions

This project adheres to the Contributor Covenant [code of conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please refer to our [contributing guide](CONTRIBUTING.md) for further information.






















