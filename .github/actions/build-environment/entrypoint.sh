#!/bin/bash

# Stops script execution if a command has an error
set -e

if [ -z "$GITHUB_TOKEN" ]; then
    # If github token is provided via secret, it is in input github token.
    GITHUB_TOKEN=$INPUT_GITHUB_TOKEN
fi

if [ -n "$GITHUB_TOKEN" ]; then
    # Use the github token to authenticate the git interaction (see this Stackoverflow answer: https://stackoverflow.com/a/57229018/5379273)
    git config --global url."https://api:$GITHUB_TOKEN@github.com/".insteadOf "https://github.com/"
    git config --global url."https://ssh:$GITHUB_TOKEN@github.com/".insteadOf "ssh://git@github.com/"
    git config --global url."https://git:$GITHUB_TOKEN@github.com/".insteadOf "git@github.com:"
fi

if [ -n "$INPUT_CONTAINER_REGISTRY_USERNAME" ] && [ -n "$INPUT_CONTAINER_REGISTRY_PASSWORD" ]; then
    docker login $INPUT_CONTAINER_REGISTRY_URL -u "$INPUT_CONTAINER_REGISTRY_USERNAME" -p "$INPUT_CONTAINER_REGISTRY_PASSWORD"
fi

# Navigate to working directory, if provided
if [ -n "$INPUT_WORKING_DIRECTORY" ]; then
    cd $INPUT_WORKING_DIRECTORY
else
    cd $GITHUB_WORKSPACE
fi

# set default build args if not provided
if [ -z "$INPUT_BUILD_ARGS" ]; then
    INPUT_BUILD_ARGS="--make --test"
fi

printenv
pwd
python -u build.py $INPUT_BUILD_ARGS
