#!/bin/bash
# Pass the container run arguments to the build script

if [ -n "$GITHUB_TOKEN" ]; then
    echo "Github Token supplied"
    # Can be moved to the Dockerfile as soon as GitHub actions support passing build-args. See this discussion: https://github.community/t/feature-request-build-args-support-in-docker-container-actions/16846/9
    pip install git+https://${GITHUB_TOKEN}@github.com/mltooling/universal-build.git

    # Use the github token to authenticate the git interaction (see this Stackoverflow answer: https://stackoverflow.com/a/57229018/5379273)
    git config --global url."https://api:$GITHUB_TOKEN@github.com/".insteadOf "https://github.com/"
    git config --global url."https://ssh:$GITHUB_TOKEN@github.com/".insteadOf "ssh://git@github.com/"
    git config --global url."https://git:$GITHUB_TOKEN@github.com/".insteadOf "git@github.com:"
fi

if [ -n "$CONTAINER_REGISTRY_USERNAME" ] && [ -n "$CONTAINER_REGISTRY_TOKEN" ]; then
    docker login $CONTAINER_REGISTRY_URL -u "$CONTAINER_REGISTRY_USERNAME" -p "$CONTAINER_REGISTRY_TOKEN"
fi

python -u /github/workspace/build.py "$@"