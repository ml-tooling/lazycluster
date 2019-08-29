import os, sys
import subprocess
import argparse
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('--name', help='python package name', default="lazycluster")
parser.add_argument('--version', help='version of build (MAJOR.MINOR.PATCH-TAG)')
parser.add_argument('--notests', help="deactivate integration tests", action='store_true')
parser.add_argument('--deploy', help='deploy python package to pip', action='store_true')

args, unknown = parser.parse_known_args()
if unknown:
    print("Unknown arguments "+str(unknown))

# Wrapper to print out command
def call(command):
    print("Executing: "+command)
    return subprocess.call(command, shell=True)

# get version
if args.deploy and not args.version:
    print("Please provide a version for deployment (--version=MAJOR.MINOR.PATCH-TAG)")
    sys.exit()
elif args.deploy:
    # for deployment, use version as it is provided
    args.version = str(args.version)

if args.version:
    # Update version in __version__ to provided version
    pass

# Install develop version of packages
call("pip uninstall .")
call("pip install --ignore-installed --no-cache -U -e .")

# Update documentation
import importlib
import lazycluster.cluster.dask_cluster
import lazycluster.generate_docs as gd
generator = gd.MarkdownAPIGenerator('/lazycluster', 'https://github.com/ml-tooling/lazycluster.git')
module_body_str = generator.module2md(lazycluster.cluster.dask_cluster)
gd.to_md_file(module_body_str, './docs/cluster.dask_cluster')

if args.deploy:
    call("python3 -m pip install --user --upgrade setuptools wheel twine")
    # Deploy to PyPi
    call("python3 ./setup.py deploy")


# call("python setup.py develop")
# pip uninstall . && pip install --ignore-installed --no-cache -U -e .