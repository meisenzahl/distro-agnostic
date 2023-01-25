#!/bin/bash

docker run \
    --pull=always \
    --tty \
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
            --package io.elementary.desktop
    "
