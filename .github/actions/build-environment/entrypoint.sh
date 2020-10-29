#!/bin/bash

# Stops script execution if a command has an error
set -e

ADDITIONAL_BUILD_ARGS=""

if [ -n "$GITHUB_TOKEN" ]; then
    # Use the github token to authenticate the git interaction (see this Stackoverflow answer: https://stackoverflow.com/a/57229018/5379273)
    git config --global url."https://api:$GITHUB_TOKEN@github.com/".insteadOf "https://github.com/"
    git config --global url."https://ssh:$GITHUB_TOKEN@github.com/".insteadOf "ssh://git@github.com/"
    git config --global url."https://git:$GITHUB_TOKEN@github.com/".insteadOf "git@github.com:"

    ADDITIONAL_BUILD_ARGS="$ADDITIONAL_BUILD_ARGS --github-token=$GITHUB_TOKEN"
fi

if [ -n "$INPUT_CONTAINER_REGISTRY_USERNAME" ] && [ -n "$INPUT_CONTAINER_REGISTRY_PASSWORD" ]; then
    docker login $INPUT_CONTAINER_REGISTRY_URL -u "$INPUT_CONTAINER_REGISTRY_USERNAME" -p "$INPUT_CONTAINER_REGISTRY_PASSWORD"
    ADDITIONAL_BUILD_ARGS="$ADDITIONAL_BUILD_ARGS --container-registry-url=$INPUT_CONTAINER_REGISTRY_URL"
    ADDITIONAL_BUILD_ARGS="$ADDITIONAL_BUILD_ARGS --container-registry-username=$INPUT_CONTAINER_REGISTRY_USERNAME"
    ADDITIONAL_BUILD_ARGS="$ADDITIONAL_BUILD_ARGS --container-registry-password=$INPUT_CONTAINER_REGISTRY_PASSWORD"
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

if [ -n "$INPUT_PYPI_TOKEN" ]; then
    ADDITIONAL_BUILD_ARGS="$ADDITIONAL_BUILD_ARGS --pypi-token=$INPUT_PYPI_TOKEN"
fi

if [ -n "$INPUT_PYPI_TEST_TOKEN" ]; then
    ADDITIONAL_BUILD_ARGS="$ADDITIONAL_BUILD_ARGS --pypi-test-token=$INPUT_PYPI_TEST_TOKEN"
fi

printenv
pwd
echo "python -u build.py $INPUT_BUILD_ARGS $ADDITIONAL_BUILD_ARGS"