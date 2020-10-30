#!/bin/bash

# Stops script execution if a command has an error
set -e

ADDITIONAL_OPTIONS=""

if [[ $INPUT_CURRENT_COMMIT_ONLY = true ]]; then
    ADDITIONAL_OPTIONS="--exact-match"
fi

LATEST_VERSION=$(git describe --tags --match 'v[0-9].*' --abbrev=0 $ADDITIONAL_OPTIONS)

if [[ ! "$LATEST_VERSION" =~ ^v([0-9]+\.[0-9]+\.[0-9]+.*)$ ]]; then
    echo "The latest tag is not valid: $LATEST_VERSION"
    exit 1
fi

LATEST_VERSION=$(echo $LATEST_VERSION | sed -E 's/v([0-9]+\.[0-9]+\.[0-9]+.*)/\1/')

echo "::set-output name=latest_version::$LATEST_VERSION"
