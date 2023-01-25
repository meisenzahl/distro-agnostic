#!/bin/bash

docker run \
    --pull=always \
    --tty \
    --rm \
    --privileged \
    --volume /proc:/proc \
    --volume $PWD:/work \
    --workdir /work \
    archlinux:latest \
    sh -c "
        pacman -Syu --noconfirm git python-yaml && \
        ./builder \
            --distro archlinux \
            --package io.elementary.desktop
    "
