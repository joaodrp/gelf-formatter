<h1 align="center" style="border-bottom: none;">gelf-pretty</h1>
<h3 align="center">CLI to pretty-print GELF log lines</h3>
<p align="center">
    <a href="https://github.com/joaodrp/gelf-pretty/releases/latest">
        <img alt="Release" src="https://img.shields.io/github/release/joaodrp/gelf-pretty.svg">
    </a>
    <a href="https://travis-ci.com/joaodrp/gelf-pretty">
        <img alt="Travis" src="https://img.shields.io/travis/com/joaodrp/gelf-pretty.svg">
    </a>
    <a href="https://codecov.io/gh/joaodrp/gelf-pretty">
        <img alt="Codecov"
            src="https://img.shields.io/codecov/c/github/joaodrp/gelf-pretty/master.svg">
    </a>
    <a href="https://goreportcard.com/report/github.com/joaodrp/gelf-pretty">
        <img alt="Go Report" src="https://goreportcard.com/badge/github.com/joaodrp/gelf-pretty">
    </a>
    <a href="https://semver.org/">
        <img alt="SemVer" src="https://img.shields.io/badge/semver-2.0.0-blue.svg">
    </a>
    <a href="https://conventionalcommits.org">
        <img alt="Conventional Commits"
            src="https://img.shields.io/badge/conventional%20commits-1.0.0-yellow.svg">
    </a>
    <a href="LICENSE">
        <img alt="Software License" src="https://img.shields.io/badge/license-MIT-brightgreen.svg">
    </a>
    <a href="https://saythanks.io/to/joaodrp">
        <img alt="SayThanks.io" src="https://img.shields.io/badge/say%20thanks-%E2%98%BC-1EAEDB.svg">
    </a>
</p>

---

## Introduction

CLI tool to read <a href="http://docs.graylog.org/en/latest/pages/gelf.html">Graylog
Extended Log Format (GELF)</a> log lines from `stdin`, such as:

```text
{"version":"1.1","host":"my-server","short_message":"Starting server","timestamp":1555690413.839,"level":6,"_app":"my-app","_logger":"api","_port":"3000"}
{"version":"1.1","host":"my-server","short_message":"Listening for requests","timestamp":1555690413.903,"level":6,"_app":"my-app","_logger":"api","_endpoint":"locahost:3000/v1"}
{"version":"1.1","host":"my-server","short_message":"Request received","timestamp":155569049.540,"level":6,"_app":"my-app","_logger":"api","_method":"GET","_path":"/todos/1","_request_id":"0c4c165d"}
{"version":"1.1","host":"my-server","short_message":"Response","full_message":"{\n\t\"user_id\": 1,\n\t\"id\": 1,\n\t\"title\": \"fix /users/:id/todos route\",\n\t\"completed\": false\n}","timestamp":155569049.584,"level":7,"_app":"my-app","_logger":"api","_request_id":"0c4c165d","_status":200}
{"version":"1.1","host":"my-server","short_message":"Request received","timestamp":155569349.236,"level":6,"_app":"my-app","_logger":"api","_method":"GET","_path":"/users/1/todos","_request_id":"0c4c165d"}
{"version":"1.1","host":"my-server","short_message":"Unexpected error","full_message":"runtime error: index out of range\ngoroutine 1 [running]:\nmain.main()\n\t/app/api/main.go: 9 +0x20","timestamp":155569349.563,"level":3,"_app":"my-app","_logger":"api","_request_id":"0c4c165d"}
{"version":"1.1","host":"my-server","short_message":"Server shutting down","timestamp":155569349.571,"level":4,"_app":"my-app","_logger":"api"}
```

And pretty-print them to `stdout` like:

![Demo](https://user-images.githubusercontent.com/484633/56434633-4eb7d900-62cd-11e9-8ff5-27d6f4931f7a.png)

## Installation

You can install `gelf-pretty` using one of the following options:
 
- Pre-built packages for macOS and Linux (easiest);
- Pre-compiled binaries for macOS, Linux and Windows;
- From source.

### Pre-built packages
#### macOS

Install via [Homebrew](https://brew.sh/):

```bash
$ brew install joaodrp/tap/gelf-pretty
```

#### Linux

Install via [Snapcraft](https://snapcraft.io/gelf-pretty): 

```bash
$ snap install gelf-pretty
```

You can also download `.deb` or `.rpm` packages from the [releases
page](https://github.com/joaodrp/gelf-pretty/releases) and install with `dpkg
-i` or `rpm -i` respectively.

### Pre-compiled binaries

Download the correct archive for your platform from the [releases
page](https://github.com/joaodrp/gelf-pretty/releases) and extract the
`gelf-pretty` binary to a directory included in your `$PATH`/`Path`.

### From source

```bash
$ go get -u github.com/joaodrp/gelf-pretty
```
Make sure that the `$GOPATH/bin` folder is in your `$PATH`.

## Output Format

GELF messages are pretty-printed in the following format:

```text
[<timestamp>] <level>: <_app>/<_logger> on <host>: <short_message> <_*>=<value>\n
    <full_message>
```

### Description
- `<timestamp>` is the value of the standard GELF unix `timestamp` field,
  formatted as `2006-01-02 15:04:05.000`;

- `<level>` is the value of the standard GELF log `level` field, formatted in a
  human-readable form (e.g. `DEBUG` instead of `7`);

- `<_app>` is an optional *reserved* additional field. It can be used to
  identify the name of the application emitting the logs. If not provided, the
  forward slash that follows it is omitted;

- `<_logger>` is an optional *reserved* additional field. It can be used to
  identify the specific application module or logger instance that is emitting a
  given log line;

- `<host>` is the value of the standard GELF `host` field;

- `<short_message>` is the value of the standard GELF `short_message` field;

- `<_*>=<value>` is any number of GELF additional fields (`_*`), formatted as
  `key=value` pairs separated by a whitespace. The keys leading underscore is
  omitted for readability;

- `<full_message>` is the value of the standard GELF `full_message` field
  (usually used for exception backtraces). It is preceded by a new line and
  indented with four spaces.

### Colors

`gelf-pretty` automatically detects if the output stream is a `TTY` or not. If
(and only if) it is, the output will be formatted by default with ANSI colors
for improved readability.

## Usage

To pretty-print GELF logs from your application simply pipe its output to
`gelf-pretty`:

```bash
$ app | gelf-pretty
```

Run `gelf-pretty --help` for a list of available options:

```bash
$ gelf-pretty --help
Usage of gelf-pretty:
  --no-color
        Disable color output
  --version
        Show version information
```

### Capture stderr

If your application writes to the `stderr` stream you will need to pipe it along
with `stdout`:

```bash
$ app 2>&1 | gelf-pretty
```

### Disable colors

To disable colored output (even if the output stream is a `TTY`) use the
`--no-color` option:

```bash
$ app | gelf-pretty --no-color
```

## FAQ

### My logs are not formatted, why?

`gelf-pretty` validates each input line. If a line (delimited by `\n`) is not a
valid JSON string or is invalid according to the [GELF
specification](http://docs.graylog.org/en/latest/pages/gelf.html#gelf-payload-specification),
`gelf-pretty` will simply echo it back to the `stdout` without any modification
(silently, with no error messages).

If you believe that your log messages are valid, please [open a new
issue](https://github.com/joaodrp/gelf-pretty/issues/new) and let us know.

## Contributions

This project adheres to the Contributor Covenant [code of
conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this
code. Please refer to our [contributing guide](CONTRIBUTING.md) for further
information.
