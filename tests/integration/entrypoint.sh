#!/bin/bash

pip install -e .

pip install pytest

pip install docker

pip install pexpect

pytest -s /src/tests/integration/