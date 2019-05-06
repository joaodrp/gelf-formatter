# Contributing

First off, thank you for considering contributing to this project. By participating you agree to abide our [code of conduct](/CODE_OF_CONDUCT.md).

## Bugs and Questions

If you have noticed a bug or have a question, please make sure it was not already reported/asked by someone else. You can do this by [searching all issues](https://github.com/joaodrp/gelf-formatter/issues).

If you are unable to find an issue addressing the same problem, go ahead and [open a new one](https://github.com/joaodrp/gelf-formatter/issues/new). Be sure to include a clear
  description and an executable test case demonstrating the expected behavior that is not occurring.

## New Features

If you want to implement a new feature please first discuss it by raising an issue.

## Development Instructions

### Fork and Branch

Start by [forking this repository](https://help.github.com/en/articles/fork-a-repo) and creating a branch for your changes.

The name of your branch should follow this syntax:

```
[fix|feature]/<issue number>-<short-description>
```

- Use `fix` as prefix if your changes address a bug, or `feature` if you are adding a new feature;
- Make sure to include the number of the issue that was previously raised to report the issue or propose the new feature;
- Add a short but accurate description of your fix or feature (hyphenated).

### Setup

Prerequisites:

- `make`
- [Python 3.7+](https://www.python.org/downloads/)

Install development dependencies:

```
$ make setup
```

Run the test suite to make sure everything is properly setup:

```
$ make test
```

### Develop

Make your changes and run the test suite and linters:

```
$ make ci
```

#### Commit

Commit messages should adhere to the [Conventional Commits specification](https://conventionalcommits.org/).

### Create Pull Request

Push the changes to your fork and [create a Pull Request](https://help.github.com/en/articles/creating-a-pull-request) against the
master branch of this repository.
