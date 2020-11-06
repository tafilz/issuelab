import os
import re

from setuptools import setup


def get_long_description():
    """
    Return the README.
    """
    return open("README.md", "r", encoding="utf8").read()


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [
        dirpath
        for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, "__init__.py"))
    ]


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    path = os.path.join(package, "__init__.py")
    init_py = open(path, "r", encoding="utf8").read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


setup(
    name="issuelab",
    version=get_version("issuelab"),
    author="Tafil Avdyli",
    author_email="tafil@tafhub.de",
    description="Migrate issue boards",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/tafilz/issuelab",
    packages=get_packages("issuelab"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests", "python-gitlab", "youtrack"]
)
