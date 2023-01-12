import os
import pathlib
import shutil
import subprocess

from . import logger


def prepare_build_directory(distro):
    path = os.path.abspath("artifacts")
    for element in distro.split(":"):
        path = os.path.join(path, element)

    if not os.path.isdir(path):
        os.makedirs(path)


def run_cmd(cmd, cwd=os.path.dirname(os.path.realpath(__file__))):
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


def add_dependencies(dependencies):
    if len(dependencies) == 0:
        return

    cmd = "dnf install -y " + " ".join(dependencies)

    run_cmd(cmd)


def remove_dependencies(dependencies):
    pass
    # if len(dependencies) == 0:
    #     return

    # cmd = "dnf remove -y " + " ".join(dependencies) + " --no-autoremove"

    # run_cmd(cmd)


def copy(src, dst):
    if os.path.islink(src):
        linkto = os.readlink(src)

        if os.path.islink(dst):
            os.unlink(dst)

        if os.path.exists(dst):
            os.remove(dst)

        os.symlink(linkto, dst)
    else:
        shutil.copy(src, dst, follow_symlinks=False)


def add_source_dependencies(dependencies, distro):
    for dependency in dependencies:
        path = os.path.abspath("artifacts")
        for element in distro.split(":"):
            path = os.path.join(path, element)
        path = os.path.join(path, "rootfs", dependency)

        for p in list(pathlib.Path(path).rglob("*")):
            src = str(p)
            dst = str(p).replace(path, "")

            logger.debug(f"Copy {src} to {dst}")

            if os.path.isdir(src):
                if not os.path.exists(dst):
                    os.mkdir(dst)
            else:
                copy(src, dst)


def remove_source_dependencies(dependencies, distro):
    for dependency in dependencies:
        path = os.path.abspath("artifacts")
        for element in distro.split(":"):
            path = os.path.join(path, element)
        path = os.path.join(path, "rootfs", dependency)

        for p in list(pathlib.Path(path).rglob("*")):
            src = str(p)
            dst = str(p).replace(path, "")

            if not os.path.isdir(src) and os.path.exists(dst):
                logger.debug(f"Delete {dst}")
                os.remove(dst)


def download_git_source(name, source, distro):
    tag = source.get("tag", None)
    url = source.get("url", None)
    repo_name = url.split("/")[-1]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-3]

    download_directory = os.path.abspath("artifacts")
    for element in distro.split(":"):
        download_directory = os.path.join(download_directory, element)
    download_directory = os.path.join(download_directory, "downloads", name, tag)

    if not os.path.exists(download_directory):
        os.makedirs(download_directory)

    safe_url = []
    for part in url.replace("/", "_").replace(":", "_").replace("@", "_").split("_"):
        if part:
            safe_url.append(part)

    safe_url = "_".join(safe_url)

    repo_dir = os.path.join(download_directory, safe_url)

    cmd = f"git clone --branch {tag} --single-branch --depth 1 {url} {repo_dir}"

    if not os.path.exists(repo_dir):
        run_cmd(cmd)

    return repo_dir


def build_meson(package, download_path, distro):
    name = package["name"]

    build_directory = os.path.abspath("artifacts")
    for element in distro.split(":"):
        build_directory = os.path.join(build_directory, element)
    build_directory = os.path.join(build_directory, "build")

    if not os.path.isdir(build_directory):
        os.makedirs(build_directory)

    build_directory = os.path.join(build_directory, name)

    rootfs_directory = os.path.abspath("artifacts")
    for element in distro.split(":"):
        rootfs_directory = os.path.join(rootfs_directory, element)
    rootfs_directory = os.path.join(rootfs_directory, "rootfs", name)

    install_directory = os.path.join(rootfs_directory, "usr")

    cmd = f"meson {build_directory} --prefix={install_directory}"

    run_cmd(cmd, cwd=download_path)

    if not os.path.exists(rootfs_directory):
        os.makedirs(rootfs_directory)

    cmd = f"ninja -C {build_directory} install"

    run_cmd(cmd, cwd=download_path)


def build_image(package, dependencies, distro):
    name = package["name"]

    rootfs_directory = os.path.abspath("artifacts")
    for element in distro.split(":"):
        rootfs_directory = os.path.join(rootfs_directory, element)
    rootfs_directory = os.path.join(rootfs_directory, "rootfs")

    rootfs_image_directory = os.path.join(rootfs_directory, name)

    if os.path.exists(rootfs_image_directory):
        shutil.rmtree(rootfs_image_directory)

    os.makedirs(rootfs_image_directory)

    for dependency in dependencies:
        if dependency == name:
            continue

        path = os.path.join(rootfs_directory, dependency)

        for p in list(pathlib.Path(path).rglob("*")):
            src = str(p)
            dst = str(p).replace(path, "")
            if dst.startswith("/"):
                dst = os.path.join(rootfs_image_directory, dst[1:])
            else:
                dst = os.path.join(rootfs_image_directory, dst)

            logger.debug(f"Copy {src} to {dst}")

            if os.path.isdir(src):
                if not os.path.exists(dst):
                    os.mkdir(dst)
            else:
                copy(src, dst)


def build_package(package, available_packages, distro):
    name = package["name"]

    path = os.path.abspath("artifacts")
    for element in distro.split(":"):
        path = os.path.join(path, element)
    path = os.path.join(path, "rootfs", name)

    if os.path.isdir(path):
        return

    dependencies = []
    source_dependencies = []
    for dependency in package.get("dependencies", []):
        if dependency in available_packages:
            source_dependencies.append(dependency)
        else:
            dependencies.append(dependency)

    type = package.get("type", "")
    if type == "image":
        build_image(dependencies, source_dependencies, distro)
        return

    buildsystem = package.get("buildsystem", "")
    if buildsystem == "meson":
        dependencies.extend(
            [
                "meson",
                "ninja-build",
            ]
        )

    logger.debug("  dependencies:")
    for dependency in dependencies:
        logger.debug(f"    {dependency}")

    logger.debug("  source_dependencies:")
    for dependency in source_dependencies:
        logger.debug(f"    {dependency}")

    add_dependencies(dependencies)

    add_source_dependencies(source_dependencies, distro)

    for source in package.get("sources", []):
        type = source.get("type", "")

        download_path = None
        if type == "git":
            download_path = download_git_source(name, source, distro)

        if buildsystem == "meson":
            build_meson(package, download_path, distro)

    remove_source_dependencies(source_dependencies, distro)

    remove_dependencies(dependencies)
