#!/bin/bash

PACKAGE=$1

docker run \
    --pull=always \
    --tty \
    --interactive \
    --rm \
    --privileged \
    --volume /proc:/proc \
    --volume $PWD:/work \
    --workdir /work \
    fedora:40 \
    sh -c "
        dnf install -y git python3 && \
        ./builder \
            --distro fedora:40 \
            --package ${PACKAGE}
    "
