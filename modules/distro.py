import os
import subprocess
import yaml

from . import logger


class Distro:
    def __init__(self, name, package_manager, packages):
        self._name = name
        self._package_manager = package_manager
        self._packages = packages

    @property
    def name(self):
        return self._name

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
            cmd = "apt-get install -y " + " ".join(packages)

            self._run_cmd(cmd)
        elif self._package_manager == "pacman":
            cmd = "pacman -Syu --noconfirm " + " ".join(packages)

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
    for filename in os.listdir(distros_dir):
        path = os.path.join(distros_dir, filename)
        with open(path, "r") as f:
            available_distro = yaml.safe_load(f)

            name = available_distro["name"]
            if not name:
                logger.critical(f"No name provided in {path}")

            package_manager = available_distro["package-manager"]
            if not package_manager:
                logger.critical(f"No package-manager provided in {path}")

            packages = available_distro["packages"]
            if not packages:
                logger.critical(f"No packages provided in {path}")

            if name in available_distros:
                logger.critical(f"Found multiple recipes for {name}")

            available_distros[name] = Distro(name, package_manager, packages)

    return available_distros


def get_distro(name):
    return get_available_distros()[name]
