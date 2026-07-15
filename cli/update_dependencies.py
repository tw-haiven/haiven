# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - only used on older Python versions
    tomllib = None

try:
    import toml
except ModuleNotFoundError:
    toml = None


def update_package(package_name, group=None):
    if group:
        os.system(f"poetry add --group {group} {package_name}@latest")
    else:
        os.system(f"poetry add {package_name}@latest")


def get_packages_from_pyproject(pyproject_path):
    if tomllib is not None:
        with open(pyproject_path, "rb") as file:
            pyproject = tomllib.load(file)
    elif toml is not None:
        with open(pyproject_path, "r", encoding="utf-8") as file:
            pyproject = toml.load(file)
    else:
        raise ModuleNotFoundError(
            "No TOML parser available. Use Python 3.11+ or install the toml package."
        )

    dependencies = pyproject.get("tool", {}).get("poetry", {}).get("dependencies", {})
    dev_dependencies = (
        pyproject.get("tool", {})
        .get("poetry", {})
        .get("group", {})
        .get("dev", {})
        .get("dependencies", {})
    )

    # Exclude python version specification
    if "python" in dependencies:
        del dependencies["python"]

    return list(dependencies.keys()), list(dev_dependencies.keys())


if __name__ == "__main__":
    pyproject_path = "pyproject.toml"

    if os.path.exists(pyproject_path):
        dependencies, dev_dependencies = get_packages_from_pyproject(pyproject_path)

        for package in dependencies:
            update_package(package)

        for dev_package in dev_dependencies:
            update_package(dev_package, group="dev")
    else:
        print(f"{pyproject_path} not found.")
