import os
from typing import Dict, Union

from universal_build import build_utils
from universal_build.helpers import build_python

MAIN_PACKAGE = "lazycluster"
GITHUB_URL = "https://github.com/ml-tooling/lazycluster"

HERE = os.path.abspath(os.path.dirname(__file__))

TEST_DIRECTORY_PATH = "tests"


def main(args: Dict[str, Union[bool, str]]) -> None:

    # set current path as working dir
    os.chdir(HERE)

    version = args.get(build_utils.FLAG_VERSION)

    if version:
        # Update version in _about.py
        build_python.update_version(
            os.path.join(HERE, f"src/{MAIN_PACKAGE}/_about.py"),
            str(version),
            exit_on_error=True,
        )

    if args[build_utils.FLAG_MAKE]:
        # Install pipenv dev requirements
        build_python.install_build_env(exit_on_error=True)
        # Create API documentation via lazydocs
        build_python.generate_api_docs(
            github_url=GITHUB_URL, main_package=MAIN_PACKAGE, exit_on_error=True
        )
        # Build distribution via setuptools
        build_python.build_distribution(exit_on_error=True)

    if args[build_utils.FLAG_CHECK]:
        build_python.code_checks(exit_on_error=True, safety=False)

    if args.get(build_utils.FLAG_TEST):
        # Remove coverage files
        build_utils.run("pipenv run coverage erase", exit_on_error=False)

        test_markers = args.get(build_utils.FLAG_TEST_MARKER)

        if (
            isinstance(test_markers, list)
            and build_utils.TEST_MARKER_SLOW in test_markers
        ):
            # Run if slow test marker is set: test in multiple environments
            # Python 3.6
            build_python.test_with_py_version(
                python_version="3.6.12", exit_on_error=True
            )

            # Python 3.7
            build_python.test_with_py_version(
                python_version="3.7.9", exit_on_error=True
            )

            # Activated Python Environment (3.8)
            build_python.install_build_env()
            # Run pytest in pipenv environment
            build_utils.run("pipenv run pytest", exit_on_error=True)

            # Update pipfile.lock when all tests are successfull (lock environment)
            build_utils.run("pipenv lock", exit_on_error=True)
        else:
            # Run fast tests
            build_utils.run('pipenv run pytest -m "not slow"', exit_on_error=True)

    if args[build_utils.FLAG_RELEASE]:
        build_python.publish_pypi_distribution(
            pypi_token=args.get(build_python.FLAG_PYPI_TOKEN),
            pypi_repository=args.get(build_python.FLAG_PYPI_REPOSITORY),
        )


if __name__ == "__main__":
    args = build_utils.parse_arguments()
    main(args)
