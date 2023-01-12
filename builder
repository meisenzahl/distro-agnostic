#!/usr/bin/env python3
import argparse
import os

from modules import build, logger, recipes


def main(args):
    logger.info(
        f"Building {args.package} for {args.distro} with {args.package_manager}"
    )

    logger.info(f"Scanning available packages in {args.recipes}")
    available_packages = recipes.get_available_packages(args.recipes)
    recipes.assert_can_build(args.package, available_packages)

    logger.info(f"Calculating build order")
    build_order = recipes.get_build_order(args.package, available_packages)

    logger.info(f"Preparing build directory")
    build.prepare_build_directory(args.distro)

    logger.info(f"Building packages")
    for package in build_order:
        logger.info(f"Building package {package['name']}")
        build.build_package(package, available_packages, args.distro)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--distro", default="fedora:37")
    parser.add_argument("-m", "--package-manager", default="dnf")
    parser.add_argument("-p", "--package", default="io.elementary.desktop")
    parser.add_argument("-r", "--recipes", default=os.path.abspath("recipes"))

    # try:
    main(parser.parse_args())
    # except Exception as e:
    #     logger.critical(str(e))
