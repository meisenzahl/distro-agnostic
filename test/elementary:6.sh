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
    elementary/docker:odin-stable \
    sh -c "
        apt-get update && \
        apt-get install -y git python3-yaml  && \
        export DEBIAN_FRONTEND=noninteractive && \
        ./builder \
            --distro elementary:6 \
            --package ${PACKAGE}
    "
