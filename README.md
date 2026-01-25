<h1 align="center" style="border-bottom: none;">GELF Formatter</h1>
<h3 align="center">
    <a href="http://docs.graylog.org/en/latest/pages/gelf.html">Graylog Extended Log Format (GELF)</a> formatter for the<br>Python standard library <a href="https://docs.python.org/3/library/logging.html">logging</a> module
</h3>
<p align="center">
    <a href="https://pypi.org/project/gelf-formatter/">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/gelf-formatter.svg">
    </a>
    <a href="https://pypi.org/project/gelf-formatter/">
        <img alt="Python versions" src="https://img.shields.io/pypi/pyversions/gelf-formatter.svg">
    </a>
    <a href="https://github.com/joaodrp/gelf-formatter/actions/workflows/ci.yml">
        <img alt="CI" src="https://github.com/joaodrp/gelf-formatter/actions/workflows/ci.yml/badge.svg">
    </a>
    <a href="LICENSE">
        <img alt="License" src="https://img.shields.io/badge/license-MIT-brightgreen.svg">
    </a>
</p>

---

## Motivation

There are several packages available providing *handlers* for the standard library logging module that can send application logs to [Graylog](https://www.graylog.org/) by TCP/UDP/HTTP ([py-gelf](https://pypi.org/project/pygelf/) is a good example). Although these can be useful, it's not ideal to make an application performance dependent on network requests just for the purpose of delivering logs.

Alternatively, one can simply log to a file or `stdout` and have a collector (like [Fluentd](https://www.fluentd.org/)) processing and sending those logs *asynchronously* to a remote server (and not just to Graylog, as GELF can be used as a generic log format), which is a common pattern for containerized applications. In a scenario like this all we need is a GELF logging *formatter*.

## Features

- Support for arbitrary additional fields
- Support for including reserved [`logging.LogRecord`](https://docs.python.org/3/library/logging.html#logrecord-attributes) attributes as additional fields
- Exceptions detection with traceback formatting
- Full type annotations (PEP 561 compatible)
- Zero dependencies and tiny footprint

## Installation

```sh
pip install gelf-formatter
```

## Usage

Create a `GelfFormatter` instance and pass it to [`logging.Handler.setFormatter`](https://docs.python.org/3/library/logging.html#logging.Handler.setFormatter):

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

Alternatively, configure a local [`logging.Logger`](https://docs.python.org/3/library/logging.html#logging.Logger) instance through [`logging.Logger.addHandler`](https://docs.python.org/3/library/logging.html#logging.Logger.addHandler):

```python
logger = logging.getLogger('my-app')
logger.addHandler(handler)
```

That's it. You can now use the logging module as usual, all records will be formatted as GELF messages.

### Standard Fields

The formatter outputs all (non-deprecated) fields described in the [GELF Payload Specification (version 1.1)](http://docs.graylog.org/en/latest/pages/gelf.html#gelf-payload-specification):

- `version`: String, always set to `1.1`
- `host`: String, the output of [`socket.gethostname`](https://docs.python.org/3/library/socket.html#socket.gethostname) at initialization
- `short_message`: String, log record message
- `full_message` (*optional*): String, formatted exception traceback (if any)
- `timestamp`: Number, time in seconds since the epoch as a floating point
- `level`: Integer, *syslog* severity level

None of these fields can be ignored, renamed or overridden.

#### Example

```python
logging.info("Some message")
```

```json
{"version":"1.1","host":"my-server","short_message":"Some message","timestamp":1557342545.1067393,"level":6}
```

#### Exceptions

The `full_message` field is used to store the traceback of exceptions. Log them with [`logging.exception`](https://docs.python.org/3/library/logging.html#logging.exception).

```python
import urllib.request

req = urllib.request.Request('http://www.pythonnn.org')
try:
    urllib.request.urlopen(req)
except urllib.error.URLError as e:
    logging.exception(e.reason)
```

```json
{"version": "1.1", "short_message": "[Errno -2] Name or service not known", "timestamp": 1557342714.0695107, "level": 3, "host": "my-server", "full_message": "Traceback (most recent call last):\n  ...(truncated)... raise URLError(err)\nurllib.error.URLError: <urlopen error [Errno -2] Name or service not known>"}
```

### Additional Fields

The GELF specification allows arbitrary additional fields, with keys prefixed with an underscore.

To include additional fields use the standard logging `extra` keyword. Keys will be automatically prefixed with an underscore (if not already).

```python
logging.info("request received", extra={"path": "/orders/1", "method": "GET"})
```

```json
{"version": "1.1", "short_message": "request received", "timestamp": 1557343604.5892842, "level": 6, "host": "my-server", "_path": "/orders/1", "_method": "GET"}
```

#### Reserved Fields

By default the formatter ignores all [`logging.LogRecord` attributes](https://docs.python.org/3/library/logging.html#logrecord-attributes). You can opt to include them as additional fields using `allowed_reserved_attrs`:

```python
formatter = GelfFormatter(allowed_reserved_attrs=["lineno", "module", "filename"])

logging.debug("starting application...")
```

```json
{"version": "1.1", "short_message": "starting application...", "timestamp": 1557346554.989846, "level": 6, "host": "my-server", "_lineno": 175, "_module": "myapp", "_filename": "app.py"}
```

Similarly, you can ignore additional attributes passed via `extra` using `ignored_attrs`:

```python
formatter = GelfFormatter(ignored_attrs=["secret", "password"])

logging.debug("app config", extra={"connection": "local", "secret": "verySecret!"})
```

```json
{"version": "1.1", "short_message": "app config", "timestamp": 1557346554.989846, "level": 6, "host": "my-server", "_connection": "local"}
```

Note: Only root-level keys are filtered. Nested fields within objects are not filtered.

#### Context Fields

Use a [`logging.Filter`](https://docs.python.org/3/library/logging.html#filter-objects) to add context fields to all log messages:

```python
class ContextFilter(logging.Filter):
    def filter(self, record):
        record.app = "my-app"
        record.environment = os.environ.get("APP_ENV")
        return True

handler.addFilter(ContextFilter())
```

## License

MIT
