#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created based on: https://github.com/kennethreitz/setup.py/blob/master/setup.py
# Alternative: https://github.com/seanfisk/python-project-template/blob/master/setup.py.tpl
# https://github.com/pypa/sampleproject/blob/master/setup.py
# https://blog.ionelmc.ro/2014/05/25/python-packaging


from __future__ import absolute_import, print_function

import io
import os
import sys
from glob import glob
from os.path import basename, splitext

from setuptools import find_packages, setup  # type: ignore

# Package meta-data
NAME = "lazycluster"
MAIN_PACKAGE = NAME  # Change if main package != NAME
DESCRIPTION = "Distributed machine learning made simple."
URL = "https://github.com/ml-tooling/lazycluster.git"
EMAIL = "team@mltooling.org"
AUTHOR = "ML Tooling Team"
LICENSE = "Apache License 2.0"
REQUIRES_PYTHON = ">=3.6"
VERSION = (
    None  # Only set version if you like to overwrite the version in __version__.py
)

# Please define the requirements within the requirements.txt

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

# Check if version is right
if sys.version_info[:1] == 3 and sys.version_info[:2] < (3, 6):
    raise Exception("This package needs Python 3.6 or later.")

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!

with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

# Read the requirements.txt and use it as the setup.py requirements
with io.open(os.path.join(here, "requirements.txt"), encoding="utf-8") as f:
    requirements = [line.rstrip() for line in f.readlines()]

# Load the package's __version__.py module as a dictionary.
about = {}  # type: dict
if not VERSION:
    with open(os.path.join(here, os.path.join("src", MAIN_PACKAGE), "about.py")) as f:  # type: ignore
        exec(f.read(), about)
else:
    about["__version__"] = VERSION

# Where the magic happens:
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description="%s\n\nRequirements:\n%s" % (long_description, requirements),
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    license=LICENSE,
    packages=find_packages(where="src", exclude=("tests", "test")),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    classifiers=[
        # TODO: Update via https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    package_data={
        # If there are data files included in your packages that need to be
        # 'sample': ['package_data.dat'],
    },
    project_urls={
        "Changelog": URL + "/blob/main/CHANGELOG.md",
        "Issue Tracker": URL + "/issues",
        "Source": URL,
    },
    entry_points={
        # 'console_scripts': ['cli-command=my_package.cli_handler:cli'],
    },
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    extras_require={},
    setup_requires=[],
)
