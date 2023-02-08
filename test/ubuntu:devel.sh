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
    ubuntu:devel \
    sh -c "
        apt-get update && \
        apt-get install -y git python3-yaml  && \
        export DEBIAN_FRONTEND=noninteractive && \
        ./builder \
            --distro ubuntu:devel \
            --package ${PACKAGE}
    "
