#!/bin/bash

docker run \
    --pull=always \
    --tty \
    --rm \
    --privileged \
    --volume /proc:/proc \
    --volume $PWD:/work \
    --workdir /work \
    ubuntu:22.04 \
    sh -c "
        apt-get update && \
        apt-get install -y git python3-yaml  && \
        export DEBIAN_FRONTEND=noninteractive && \
        ./builder \
            --distro ubuntu:22.04 \
            --package io.elementary.desktop
    "
