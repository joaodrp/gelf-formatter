# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name="gelf-formatter",
    version="0.1.0",
    description="GELF formatter for the standard Python logging module",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/joaodrp/py-gelf-formatter",
    author="João Pereira",
    license="MIT",
    keywords=["gelf", "graylog", "logger", "logging", "log", "json"],
    classifiers=[
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
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    python_requires=">=2.7",
    install_requires=["python-json-logger>=0.1.11"],
)
