import logging
import sys
import os

import click

from typing import Optional, List
import storm.__main__ as storm

from lazycluster import RuntimeManager, NoRuntimesDetectedError

log = logging.getLogger(__name__)


@click.group()
@click.version_option()
def cli():
    # log to sys out
    logging.basicConfig(stream=sys.stdout, format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


@cli.command('add-runtime')
@click.argument("name")
@click.argument("connection_uri")
@click.option("--id_file", "-id", required=False, type=click.STRING,
              help="The private key file that should be used for authentication")
@click.option("--options", "-o", required=False, default=[], help="Custom ssh options")
@click.option("--config", "-c", required=False, type=click.STRING, help="The ssh config file")
def add_runtime(name: str, connection_uri: str, id_file: Optional[str] = None, options: List = [], config: Optional[str] = None):
    storm.add(name, connection_uri, id_file, options, config)


@cli.command('delete-runtime')
@click.argument("name")
@click.option("--config", "-c", required=False, type=click.STRING, help="The ssh config file")
def delete_runtimes(name: str, config: Optional[str] = None):
    # Delete the related ssh config
    storm.delete(name, config)

    # Delete configured remote kernel if present
    try:
        import remote_ikernel

        kernel_name = 'rik_ssh_' + name.replace('-', '_') + '_py36'

        os.system('remote_ikernel manage --delete ' + kernel_name)

        # The Identity file won't be removed. Maybe it is useful to provide an additional flag to enforce the removal
        # can be retrieved from storm via single_ssh_entry['options']['identityfile']
    except Exception:
        pass

    print('Runtime successfully deleted.')


@cli.command('list-runtimes')
def list_runtime():

    try:
        runtime_group = RuntimeManager().create_group()
    except NoRuntimesDetectedError:
        print('\nNo runtimes detected!')
        return

    # Accessing an info attribute will enforce the actual reading of the data via ssh. Since the reading causes
    # many prints to the console we enforce this before actually printing the desired output.json.loads
    for runtime in runtime_group.runtimes:
        runtime.info

    runtime_group.cleanup()

    print('\n\u001b[1m')
    print(str(runtime_group.runtime_count) + ' Runtimes detected:')
    print('\u001b[0m')

    runtime_group.print_runtime_info()

    print('\n')


@cli.command('start-dask')
def start_dask_cluster():
    from lazycluster.cluster import DaskCluster
    cluster = DaskCluster(RuntimeManager().create_group())
    cluster.start()
    while True:
        pass


if __name__ == '__main__':
    cli()