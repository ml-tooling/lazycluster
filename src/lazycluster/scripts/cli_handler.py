import logging
import os
import sys
from typing import List, Optional

import click
import storm.__main__ as storm
from click_spinner import spinner

from lazycluster import NoRuntimesDetectedError, RuntimeManager

log = logging.getLogger(__name__)


@click.group()
@click.version_option()
@click.option("--debug/--no-debug", "-d", default=False)
def cli(debug: bool) -> None:
    # log to sys out
    log_level = logging.DEBUG if debug else logging.CRITICAL
    logging.basicConfig(
        stream=sys.stdout,
        format="%(asctime)s : %(levelname)s : %(message)s",
        level=logging.CRITICAL,
    )
    logging.getLogger("paramiko").setLevel(logging.CRITICAL)
    logging.getLogger("lazycluster").setLevel(log_level)


@cli.command("add-runtime")
@click.argument("name")
@click.argument("connection_uri")
@click.option(
    "--id_file",
    "-id",
    required=False,
    type=click.STRING,
    help="The private key file that should be used for authentication",
)
@click.option("--options", "-o", required=False, default=[], help="Custom ssh options")
@click.option(
    "--config", "-c", required=False, type=click.STRING, help="The ssh config file"
)
def add_runtime(
    name: str,
    connection_uri: str,
    id_file: Optional[str] = None,
    options: List = [],
    config: Optional[str] = None,
) -> None:
    storm.add(name, connection_uri, id_file, options, config)


@cli.command("delete-runtime")
@click.argument("name")
@click.option(
    "--config", "-c", required=False, type=click.STRING, help="The ssh config file"
)
def delete_runtimes(name: str, config: Optional[str] = None) -> None:
    # Delete the related ssh config
    storm.delete(name, config)

    # Delete configured remote kernel if present
    try:
        import remote_ikernel  # noqa: F401

        kernel_name = "rik_ssh_" + name.replace("-", "_") + "_py36"

        os.system("remote_ikernel manage --delete " + kernel_name)

        # The Identity file won't be removed. Maybe it is useful to provide an additional flag to enforce the removal
        # can be retrieved from storm via single_ssh_entry['options']['identityfile']
    except Exception:
        pass

    print("Runtime successfully deleted.")


@cli.command("list-runtimes")
@click.option(
    "--long", "-l", is_flag=True, help="Print detailed information about the Runtimes"
)
def list_runtime(long: bool) -> None:
    with spinner():

        try:
            runtime_mgr = RuntimeManager()
        except NoRuntimesDetectedError:
            print("\nNo runtimes detected!\n")
            return

        if long:
            # Ensure that all runtime info are read asynchronously before printing.
            # Otherwise each runtime will read its information synchronously.
            runtime_mgr._group.fill_runtime_info_buffers_async()

    if long:
        runtime_mgr.print_runtime_info()
    else:
        # Only printing the hosts is much faster than reading the detailed host information
        runtime_mgr.print_hosts()


@cli.command("start-dask")
def start_dask_cluster() -> None:
    from lazycluster.cluster.dask_cluster import DaskCluster

    cluster = DaskCluster(RuntimeManager().create_group())
    cluster.start()
    while True:
        pass


if __name__ == "__main__":
    cli()
