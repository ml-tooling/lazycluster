import os, sys
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--name', help='python package name', default="lazycluster")
parser.add_argument('--version', help='version of build (MAJOR.MINOR.PATCH-TAG)')
parser.add_argument('--notests', help="deactivate integration tests", action='store_true')
parser.add_argument('--deploy', help='deploy python package to pip', action='store_true')

args, unknown = parser.parse_known_args()
if unknown:
    print("Unknown arguments " + str(unknown))


# Wrapper to print out command
def call(command):
    print("Executing: " + command)
    return subprocess.call(command, shell=True)


def update_version_file(version: str):
    # Update version in __version__ to provided version
    version_list = version.split('.')

    if len(version_list) != 3:
        print("Version must be provides in the format --version=MAJOR.MINOR.PATCH-TAG")
        sys.exit()

    version_str = "VERSION = ({major}, {minor}, {patch})  # must be the first line because of build.py \n" \
        .format(major=version_list[0], minor=version_list[1], patch=version_list[2])

    # Read lines of file
    f = open("__version__.py", "r")
    lines = f.readlines()
    f.close()
    # and remove it
    os.remove("__version__.py")
    # Create a new file and create new first line and append the rest again
    f = open("__version__.py", "w+")
    f.write(version_str)
    for line in lines:
        f.write(line + '\n')
    f.close()


# Get version
if args.deploy and not args.version:
    print("Please provide a version for deployment (--version=MAJOR.MINOR.PATCH-TAG)")
    sys.exit()
elif args.deploy:
    # for deployment, use version as it is provided
    args.version = str(args.version)

if args.version:
    update_version_file(str(args.version))

# Install develop version of packages
call("pip uninstall -y lazycluster")
call("pip install --ignore-installed --no-cache -U -e .")

# Update documentation
from lazycluster import generate_docs as gd
generator = gd.MarkdownAPIGenerator('/lazycluster', 'https://github.com/ml-tooling/lazycluster.git')
import lazycluster.runtimes
markdown_str = generator.module2md(lazycluster.runtimes)
gd.to_md_file(markdown_str, './docs/runtimes')

import lazycluster.runtime_mgmt
markdown_str = generator.module2md(lazycluster.runtime_mgmt)
gd.to_md_file(markdown_str, './docs/runtime_mgmt')

import lazycluster.exceptions
markdown_str = generator.module2md(lazycluster.exceptions)
gd.to_md_file(markdown_str, './docs/exceptions')

import lazycluster.cluster.runtime_cluster
markdown_str = generator.module2md(lazycluster.cluster.runtime_cluster)
gd.to_md_file(markdown_str, './docs/cluster.runtime_cluster')

import lazycluster.cluster.dask_cluster
markdown_str = generator.module2md(lazycluster.cluster.dask_cluster)
gd.to_md_file(markdown_str, './docs/cluster.dask_cluster')

import lazycluster.cluster.hyperopt_cluster
markdown_str = generator.module2md(lazycluster.cluster.hyperopt_cluster)
gd.to_md_file(markdown_str, './docs/cluster.hyperopt_cluster')

import lazycluster.cluster.exceptions
markdown_str = generator.module2md(lazycluster.cluster.exceptions)
gd.to_md_file(markdown_str, './docs/cluster.exceptions')

if args.deploy:
    call("python3 -m pip install --user --upgrade setuptools wheel twine")
    # Deploy to PyPi
    call("python3 ./setup.py deploy")