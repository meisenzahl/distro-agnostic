import os
import subprocess
import yaml

from . import logger


class Distro:
    def __init__(self, name, package_manager, packages):
        self._name = name
        self._package_manager = package_manager
        self._packages = packages or {}

    @property
    def name(self):
        return self._name

    @property
    def package_manager(self):
        return self._package_manager

    @property
    def packages(self):
        return self._packages

    def update_sources(self):
        if self._package_manager == "apt":
            self._run_cmd("apt-get update")
        else:
            logger.critical(
                f"Package manager {self._package_manager} is not supported")

    def get_packages(self, packages):
        mapped_packages = []

        for package in packages:
            mapped_package = package
            if package in self._packages:
                mapped_package = self._packages[package]

                if len(mapped_package) == 0:
                    logger.debug(f"Skipped package {package}")
                    continue

                logger.debug(f"Mapped package {package} to {mapped_package}")

            if mapped_package not in mapped_packages:
                mapped_packages.append(mapped_package)

        return mapped_packages

    def install_packages(self, packages):
        if len(packages) == 0:
            return

        if self._package_manager == "apt":
            cmd = "apt-get install --no-install-suggests -y " + " ".join(packages)

            self._run_cmd(cmd)
        elif self._package_manager == "dnf":
            cmd = "dnf install -y " + " ".join(packages)

            self._run_cmd(cmd)
        else:
            logger.critical(
                f"Package manager {self._package_manager} is not supported")

    def remove_packages(self, packages):
        pass

    def _run_cmd(self, cmd, cwd=os.path.dirname(os.path.realpath(__file__))):
        p = subprocess.Popen(
            cmd.split(" "), cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        with p.stdout:
            try:
                for line in iter(p.stdout.readline, b""):
                    logger.debug(line.decode("utf-8").rstrip())
            except subprocess.CalledProcessError as e:
                logger.critical(str(e))

        exitcode = p.wait()

        if exitcode != 0:
            logger.handle_exit(exitcode)


def get_available_distros(distros_dir="distros"):
    available_distros = {}
    extending_distros = {}
    for filename in os.listdir(distros_dir):
        path = os.path.join(distros_dir, filename)
        with open(path, "r") as f:
            available_distro = yaml.safe_load(f)

            name = available_distro["name"]
            if not name:
                logger.critical(f"No name provided in {path}")

            extends = available_distro.get("extends", None)

            package_manager = available_distro.get("package-manager", None)
            if not package_manager and not extends:
                logger.critical(f"No package-manager provided in {path}")

            packages = available_distro.get("packages", None)
            if not packages and not extends:
                logger.critical(f"No packages provided in {path}")

            if name in available_distros or name in extending_distros:
                logger.critical(f"Found multiple recipes for {name}")

            if extends:
                extending_distros[name] = {
                    "extends": extends,
                    "distro": Distro(name, package_manager, packages)
                }
            else:
                available_distros[name] = Distro(name, package_manager, packages)

    for name in extending_distros.keys():
        base_name = extending_distros[name]["extends"]
        if not base_name in available_distros:
            logger.critical(f"No distro config for base of {name} found")

        distro = extending_distros[name]["distro"]

        base_distro = available_distros[base_name]

        packages = base_distro.packages

        for key in distro.packages.keys():
            packages[key] = distro.packages[key]

        available_distros[name] = Distro(
            distro.name,
            distro.package_manager or base_distro.package_manager,
            packages
        )

    return available_distros


def get_distro(name):
    available_distros = get_available_distros()
    if name in available_distros:
        return available_distros[name]

    elements = name.split(":")
    if len(elements) == 2:
        for distro_name in available_distros.keys():
            n, v = elements

            if n == distro_name:
                logger.info(f"Using {distro_name} as config for {name}")
                distro = available_distros[distro_name]
                distro._name = name
                return distro

    logger.critical(f"Unable to provide a distro config for {name}")
