from datetime import date
from typing import Dict, List
import sys
import uuid

import click
import colorlog
import digitalocean
import toml

from goutte import __version__

log = colorlog.getLogger(__name__)
token = None


@click.command(help='DigitalOcean snapshot automation.')
@click.argument('config', envvar='GOUTTE_CONFIG', type=click.File('r'))
@click.argument('do_token', envvar='GOUTTE_DO_TOKEN')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.version_option(version=__version__)
def entrypoint(config: click.File, do_token: str, debug: bool) -> None:
    """Command line interface entrypoint"""
    global token
    if debug:
        log.setLevel('DEBUG')
    log.info('Starting goutte v{}'.format(__version__))
    token = do_token
    conf = _load_config(config)
    log.debug(f'Retention is set to {conf["retention"]} snapshots')
    droplets = _get_droplets(conf['droplets']['names'])
    try:
        if droplets:
            log.debug(f'Found {len(droplets)} matching droplets')
            for droplet in droplets:
                log.debug(f'Processing {droplet.name}')
                _snapshot_droplet(droplet)
                _prune_droplet_snapshots(droplet, conf['retention'])
        else:
            log.warn('No matching droplet found')
    except InterruptedError:
        log.critical('Received interuption signal')
        sys.exit(1)


def _load_config(config: click.File) -> Dict[str, Dict]:
    """Return a config dict from a toml config file"""
    try:
        # TODO check minimum validity (retention)
        log.debug('Loading config from {}'.format(config.name))
        return toml.load(config)
    except TypeError as e:
        log.critical('Could not read conf {}: {}'.format(config.name, e))
        sys.exit(1)
    except toml.TomlDecodeError as e:
        log.critical('Could not parse toml in config from {}: {}'
                     .format(config.name, e))
        sys.exit(1)


def _get_droplets(names: List[str]) -> List[digitalocean.Droplet]:
    """Get the droplets objects from the configuration doplets names"""
    try:
        manager = digitalocean.Manager(token=token)
        droplets = manager.get_all_droplets()
        return [droplet for droplet in droplets if droplet.name in names]
    except digitalocean.baseapi.TokenError as e:
        log.error(f'Token not valid: {e}')
    except digitalocean.baseapi.DataReadError as e:
        log.error(f'Could not read response: {e}')
    except digitalocean.baseapi.JSONReadError as e:
        log.error(f'Could not parse json: {e}')
    except digitalocean.baseapi.NotFoundError as e:
        log.error(f'Ressource not found: {e}')
    except Exception as e:
        log.error(f'Unexpected exception: {e}')


def _snapshot_droplet(droplet: digitalocean.Droplet) -> None:
    """Take a snapshot of a given droplet"""
    name = 'goutte-{}-{}-{}'.format(
        droplet.name,
        date.today().strftime('%Y%m%d'),
        uuid.uuid4().hex[:5])
    try:
        droplet.take_snapshot(name)
        log.info(f'[{droplet.name}] Snapshot ({name})')
    except digitalocean.baseapi.TokenError as e:
        log.error(f'Token not valid: {e}')
    except digitalocean.baseapi.DataReadError as e:
        log.error(f'Could not read response: {e}')
    except digitalocean.baseapi.JSONReadError as e:
        log.error(f'Could not parse json: {e}')
    except digitalocean.baseapi.NotFoundError as e:
        log.error(f'Ressource not found: {e}')
    except Exception as e:
        log.error(f'Unexpected exception: {e}')


def _prune_droplet_snapshots(droplet: digitalocean.Droplet,
                             retention: int) -> None:
    """Prune goutte snapshots if tmore than the configured retention time"""
    try:
        snapshots = [digitalocean.Snapshot.get_object(api_token=token,
                                                      snapshot_id=snapshot_id)
                     for snapshot_id in droplet.snapshot_ids]
        log.debug(f'[{droplet.name}] Exceed retention policy by '
                  f'{len(snapshots) - retention}')
        if len(snapshots) > retention:
            for snapshot in snapshots[:len(snapshots)-retention]:
                log.info(f'[{droplet.name}] Prune ({snapshot.name})')
                snapshot.destroy()
    except digitalocean.baseapi.TokenError as e:
        log.error(f'Token not valid: {e}.')
    except digitalocean.baseapi.DataReadError as e:
        log.error(f'Could not read response: {e}.')
    except digitalocean.baseapi.JSONReadError as e:
        log.error(f'Could not parse json: {e}.')
    except digitalocean.baseapi.NotFoundError as e:
        log.error(f'Ressource not found: {e}.')
    except Exception as e:
        log.error(f'Unexpected exception: {e}.')
