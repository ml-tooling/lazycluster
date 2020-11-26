#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created based on: https://github.com/kennethreitz/setup.py/blob/master/setup.py
# Alternative: https://github.com/seanfisk/python-project-template/blob/master/setup.py.tpl
# https://github.com/pypa/sampleproject/blob/master/setup.py
# https://blog.ionelmc.ro/2014/05/25/python-packaging


from __future__ import absolute_import, print_function

import os
import re
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
VERSION = None  # Only set version if you like to overwrite the version in src/_about.py


PWD = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
with open(os.path.join(PWD, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Extract the version from the _about.py module.
if not VERSION:
    with open(os.path.join(PWD, "src", MAIN_PACKAGE, "_about.py")) as f:  # type: ignore
        VERSION = re.findall(r"__version__\s*=\s*\"(.+)\"", f.read())[0]


# Where the magic happens:
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    license=LICENSE,
    packages=find_packages(where="src", exclude=("tests", "test", "docs", "examples")),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    zip_safe=False,
    install_requires=["fabric", "stormssh", "cloudpickle", "psutil", "click-spinner"],
    extras_require={
        # TODO: Add all extras (e.g. for build and test) here:
        # extras can be installed via: pip install package[dev]
        "dev": [
            "setuptools",
            "wheel",
            "twine",
            "flake8",
            "pytest",
            "pytest-mock",
            "mypy",
            "pytest-cov",
            "black",
            "pydocstyle",
            "isort",
            "lazydocs",
            "distributed",  # Dask distributed
            "hyperopt",
            "docker",
        ],
    },
    classifiers=[
        # TODO: Update based on https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    package_data={
        # If there are data files included in your packages that need to be
        # 'sample': ['package_data.dat'],
    },
    project_urls={
        "Changelog": URL + "/releases",
        "Issue Tracker": URL + "/issues",
        "Documentation": URL + "#documentation",
        "Source": URL,
    },
    entry_points={
        # 'console_scripts': ['cli-command=my_package.cli_handler:cli'],
    },
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
)
