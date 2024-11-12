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
    --env DEBIAN_FRONTEND=noninteractive \
    ubuntu:rolling \
    sh -c "
        apt-get update && \
        apt-get install -y git python3 && \
        ./builder \
            --distro ubuntu:rolling \
            --package ${PACKAGE}
    "
