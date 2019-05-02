import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(
    os.path.join(here, "gelfformatter", "__version__.py"), mode="r", encoding="utf-8"
) as f:
    exec(f.read(), about)

with open("README.md", mode="r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    url=about["__url__"],
    license=about["__license__"],
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
    install_requires=["python-json-logger>=0.1.11,<1.0.0"],
    tests_require=["mock>=2.0.0"],
)
