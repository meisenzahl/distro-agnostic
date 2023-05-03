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
    fedora:37 \
    sh -c "
        dnf install -y git python3-pyyaml && \
        ./builder \
            --distro fedora:37 \
            --package ${PACKAGE}
    "
