import os
import yaml

from . import logger


def get_available_packages():
    packages_recipes_dir = os.path.abspath("packages")
    available_packages = {}
    for filename in os.listdir(packages_recipes_dir):
        path = os.path.join(packages_recipes_dir, filename)
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

def get_build_order(distro, package, available_packages):
    available_package_names = distro.get_packages(list(available_packages.keys()))

    mapped_packages = {}
    for current_package in available_packages.keys():
        dependencies = []
        for dependency in distro.get_packages(available_packages[current_package]["dependencies"]):
            if not dependency in available_package_names:
                continue

            dependencies.append(dependency)

        mapped_packages[current_package] = dependencies

    build_order = []
    visited = set()
    def dfs(package):
        if package in visited:
            return

        if package not in mapped_packages:
            build_order.append(package)
            visited.add(package)
            return

        for dep in mapped_packages[package]:
            dfs(dep)

        build_order.append(available_packages[package])
        visited.add(package)

    dfs(package)

    return build_order
