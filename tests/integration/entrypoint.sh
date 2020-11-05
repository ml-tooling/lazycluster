#!/bin/bash

 cd /github/workspace

 pip install -e .

 pip install pytest

 pip install docker

 pip install pexpect

 pytest -s ./tests/integration/