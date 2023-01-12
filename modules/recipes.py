import os
import yaml

from . import logger


def get_available_packages(recipes_dir):
    available_packages = {}
    for filename in os.listdir(recipes_dir):
        path = os.path.join(recipes_dir, filename)
        with open(path, "r") as f:
            available_package = yaml.safe_load(f)

            name = available_package["name"]
            if not name:
                logger.critical(f"No name provided in {path}")

            logger.debug(f"    {name}")

            if name in available_packages:
                logger.critical(f"Found multiple recipes for {name}")

            available_packages[name] = available_package

    return available_packages


def assert_can_build(package, available_packages):
    for available_package_name in available_packages:
        if package == available_package_name:
            return

    logger.critical(f"No recipe available for {package}")

def get_build_order(package, available_packages):
    packages = available_packages[package]["dependencies"]
    packages.append(package)

    build_order = []
    for package in packages:
        build_order.append(available_packages[package])
        logger.debug(f"    {package}")

    return build_order
