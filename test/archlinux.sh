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
    archlinux \
    sh -c "
        pacman -Syu --noconfirm git python-yaml && \
        ./builder \
            --distro archlinux \
            --package ${PACKAGE}
    "
