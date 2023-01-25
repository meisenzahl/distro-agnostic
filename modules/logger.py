import logging
import os

from .ci import is_ci

logging.getLogger().setLevel(logging.DEBUG)

formatter = logging.Formatter("%(message)s")

console_logging = logging.StreamHandler()
if is_ci():
    console_logging.setLevel(logging.DEBUG)
else:
    console_logging.setLevel(logging.INFO)
console_logging.setFormatter(formatter)
logging.getLogger().addHandler(console_logging)

last_debugs = []

def init(distro):
    path = os.path.abspath("artifacts")
    for element in distro.split(":"):
        path = os.path.join(path, element)

    path = os.path.join(path, "builder.log")

    file_logging = logging.FileHandler(path, mode="w")
    file_logging.setLevel(logging.DEBUG)
    file_logging.setFormatter(formatter)
    logging.getLogger().addHandler(file_logging)


def debug(message):
    if not is_ci():
        last_debugs.append(message)

    logging.debug(message)


def info(message):
    last_debugs.clear()
    logging.info(message)


def warning(message):
    last_debugs.clear()
    logging.warning(message)


def error(message):
    last_debugs.clear()
    logging.error(message)


def critical(message, rc=1):
    logging.critical(message)
    handle_exit(rc)


def handle_exit(rc=0):
    if not is_ci() and rc != 0:
        for last_debug in last_debugs:
            print(last_debug)

    exit(rc)
