import os
import yaml

from collections import defaultdict

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

def get_build_order(distro, package, available_packages):
    available_package_names = distro.get_packages(list(available_packages.keys()))
    data = {}
    package_dependencies = distro.get_packages(available_packages[package]["dependencies"])
    package_dependencies.extend(distro.get_packages([package]))
    for p in package_dependencies:
        if p in available_package_names:
            dependencies = []
            for dependency in distro.get_packages(available_packages[p]["dependencies"]):
                if dependency in available_package_names:
                    dependencies.append(dependency)

            data[p] = {
                "dependencies": dependencies
            }

    build_order = []
    visited = set()
    dependencies = defaultdict(list)

    for p, package_data in data.items():
        for dependency in package_data["dependencies"]:
            dependencies[dependency].append(p)

    def dfs(p):
        if p in visited:
            return

        visited.add(p)

        for dependency in dependencies[p]:
            dfs(dependency)

        build_order.append(available_packages[p])

    for p in data:
        dfs(p)

    build_order.reverse()

    return build_order
