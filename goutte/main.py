from typing import Dict
import sys

import click
import colorlog
# import schedule
import toml

from goutte import __version__

log = colorlog.getLogger(__name__)


@click.command(help='DigitalOcean snapshot automation service')
@click.argument('config', envvar='GOUTTE_CONFIG', type=click.File('r'))
@click.argument('do_key', envvar='GOUTTE_DO_KEY')
@click.option('--oneshot', is_flag=True, help='Run all tasks and then stops')
@click.version_option(version=__version__)
def entrypoint(config: click.File, do_key: str, oneshot: bool) -> None:
    """Command line interface entrypoint"""
    log.info('Starting goutte v{}.'.format(__version__))
    assert load_config(config)


def load_config(config: click.File) -> Dict[str, Dict]:
    """Return a config dict from a toml config file"""
    try:
        log.info('Loading config from {}.'.format(config.name))
        return toml.load(config)
    except TypeError as e:
        log.critical('Could not read conf {}. {}'.format(config.name, e))
        sys.exit()
    except toml.TomlDecodeError as e:
        log.critical('Could not parse toml in config from {}. {}'
                     .format(config.name, e))
        sys.exit()
