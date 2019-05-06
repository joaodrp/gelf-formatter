# -*- coding: utf-8 -*-

import os
from io import open

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

version = {}
with open(
    os.path.join(here, "gelfformatter", "version.py"), "r", encoding="utf-8"
) as f:
    exec(f.read(), version)

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="gelf-formatter",
    version=version["__version__"],
    description="GELF formatter for the Python standard library logging module.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="João Pereira",
    url="https://github.com/joaodrp/gelf-formatter",
    license="MIT",
    keywords=["gelf", "graylog", "logger", "logging", "log", "json"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: System :: Logging",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=["gelfformatter"],
    include_package_data=True,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    tests_require=["mock>=2.0.0"],
    test_suite="tests",
)
