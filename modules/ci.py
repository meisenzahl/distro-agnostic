import os

_is_ci = None


def is_ci():
    global _is_ci

    if _is_ci != None:
        return _is_ci

    ENVIRONMENT_VARIABLES = [
        "GITHUB_ACTIONS",
        "GITLAB_CI",
    ]

    _is_ci = any(os.environ.get(e, False) for e in ENVIRONMENT_VARIABLES)

    return _is_ci
