#!/usr/bin/env python3
import argparse

from modules import build, logger, packages
from modules.distro import get_distro


def main(args):
    logger.info(f"Building {args.package} for {args.distro}")

    logger.info(f"Read distro info")
    distro = get_distro(args.distro)

    logger.info(f"Scanning available packages")
    available_packages = packages.get_available_packages()
    packages.assert_can_build(args.package, available_packages)

    logger.info(f"Calculating build order")
    build_order = packages.get_build_order(distro, args.package, available_packages)

    logger.info(f"Preparing build directory")
    build.prepare_build_directory(distro)

    logger.info(f"Building packages")
    for i in range(len(build_order)):
        package = build_order[i]
        logger.info(f"Step {i+1}/{len(build_order)}: Building package {package['name']}")
        build.build_package(package, available_packages, distro)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--distro")
    parser.add_argument("-p", "--package")

    try:
        main(parser.parse_args())
    except Exception as e:
        logger.critical(str(e))
