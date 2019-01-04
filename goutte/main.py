from datetime import date
from typing import Dict, List, Union
import sys
import uuid

import click
import colorlog
import digitalocean
import toml

from goutte import __version__

log = colorlog.getLogger(__name__)
token = None
error = 0


@click.command(help='DigitalOcean snapshots automation.')
@click.argument('config', envvar='GOUTTE_CONFIG', type=click.File('r'))
@click.argument('do_token', envvar='GOUTTE_DO_TOKEN')
@click.option('--only', type=click.Choice(['snapshot', 'prune']),
              help='Only snapshot or only prune')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.version_option(version=__version__)
def entrypoint(config: click.File, do_token: str, only: str,
               debug: bool) -> None:
    """Command line interface entrypoint"""
    global token
    if debug:
        log.setLevel('DEBUG')
    log.info('Starting goutte v{}'.format(__version__))
    token = do_token
    conf = _load_config(config)
    log.debug(f'Retention is set to {conf["retention"]} snapshots')
    if only:
        log.debug(f'Will only {only}')
    _process_droplets(conf, only)
    _process_volumes(conf, only)
    sys.exit(error)


def _load_config(config: click.File) -> Dict[str, Dict]:
    """Return a config dict from a toml config file"""
    try:
        # TODO check minimum validity (retention)
        log.debug('Loading config from {}'.format(config.name))
        conf = toml.load(config)
        assert conf['retention']
        return conf
    except TypeError as e:
        log.critical('Could not read conf {}: {}'.format(config.name, e))
        sys.exit(1)
    except toml.TomlDecodeError as e:
        log.critical('Could not parse toml in config from {}: {}'
                     .format(config.name, e))
        sys.exit(1)
    except KeyError as e:
        log.critical('Malformated configuration: {} is missing'.format(e))
        sys.exit(1)


def _process_droplets(conf: Dict[str, Union[Dict[str, str], str]],
                      only: str) -> None:
    """Execute snapshot and pruning on the droplets"""
    try:
        droplets = _get_droplets(conf['droplets']['names'])
        if droplets:
            log.debug(f'Found {len(droplets)} matching droplets')
            for droplet in droplets:
                log.debug(f'Processing {droplet.name}')
                if only == 'prune' or not only:
                    _prune_droplet_snapshots(droplet, conf['retention'])
                if only == 'snapshot' or not only:
                    _snapshot_droplet(droplet)
        else:
            log.warning('No matching droplet found')
    except KeyError:
        droplets = None
    except KeyboardInterrupt:
        log.critical('Received interuption signal')
        sys.exit(1)


def _process_volumes(conf: Dict[str, Union[Dict[str, str], str]],
                     only: str) -> None:
    """Execute snapshot and pruning on the volumes"""
    try:
        volumes = _get_volumes(conf['volumes']['names'])
        if volumes:
            log.debug(f'Found {len(volumes)} matching volumes')
            for volume in volumes:
                log.debug(f'Processing {volume.name}')
                if only == 'prune' or not only:
                    _prune_volume_snapshots(volume, conf['retention'])
                if only == 'snapshot' or not only:
                    _snapshot_volume(volume)
        else:
            log.warning('No matching volume found')
    except KeyError:
        pass
    except KeyboardInterrupt:
        log.critical('Received interuption signal')
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
    global error
    name = 'goutte-{}-{}-{}'.format(
        droplet.name,
        date.today().strftime('%Y%m%d'),
        uuid.uuid4().hex[:5])
    try:
        droplet.take_snapshot(name)
        log.info(f'{droplet.name} - Snapshot ({name})')
    except digitalocean.baseapi.TokenError as e:
        log.error(f'Token not valid: {e}.')
        error = 1
    except digitalocean.baseapi.DataReadError as e:
        log.error(f'Could not read response: {e}.')
        error = 1
    except digitalocean.baseapi.JSONReadError as e:
        log.error(f'Could not parse json: {e}.')
        error = 1
    except digitalocean.baseapi.NotFoundError as e:
        log.error(f'Ressource not found: {e}.')
        error = 1
    except Exception as e:
        log.error(f'Unexpected exception: {e}.')
        error = 1


def _prune_droplet_snapshots(droplet: digitalocean.Droplet,
                             retention: int) -> None:
    """Prune goutte snapshots if tmore than the configured retention time"""
    global error
    try:
        all_snapshots = _order_snapshots([
            digitalocean.Snapshot.get_object(
                api_token=token, snapshot_id=snapshot_id
             ) for snapshot_id in droplet.snapshot_ids
        ])
        snapshots = [snapshot for snapshot in all_snapshots
                     if snapshot.name[:6] == 'goutte']
        if len(snapshots) > retention:
            log.debug(f'{droplet.name} - Exceed retention policy by '
                      f'{len(snapshots) - retention}')
            for snapshot in snapshots[:len(snapshots)-retention]:
                log.info(f'{droplet.name} - Prune ({snapshot.name})')
                snapshot.destroy()
    except digitalocean.baseapi.TokenError as e:
        log.error(f'Token not valid: {e}.')
        error = 1
    except digitalocean.baseapi.DataReadError as e:
        log.error(f'Could not read response: {e}.')
        error = 1
    except digitalocean.baseapi.JSONReadError as e:
        log.error(f'Could not parse json: {e}.')
        error = 1
    except digitalocean.baseapi.NotFoundError as e:
        log.error(f'Ressource not found: {e}.')
        error = 1
    except Exception as e:
        log.error(f'Unexpected exception: {e}.')
        error = 1


def _get_volumes(names: List[str]) -> List[digitalocean.Volume]:
    """Get the volumes objects from the configuration volume names"""
    try:
        manager = digitalocean.Manager(token=token)
        volumes = manager.get_all_volumes()
        return [volume for volume in volumes if volume.name in names]
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


def _snapshot_volume(volume: digitalocean.Volume) -> None:
    """Take a snapshot of a given volume"""
    global error
    name = 'goutte-{}-{}-{}'.format(
        volume.name,
        date.today().strftime('%Y%m%d'),
        uuid.uuid4().hex[:5])
    try:
        volume.snapshot(name)
        log.info(f'{volume.name} - Snapshot ({name})')
    except digitalocean.baseapi.TokenError as e:
        log.error(f'Token not valid: {e}.')
        error = 1
    except digitalocean.baseapi.DataReadError as e:
        log.error(f'Could not read response: {e}.')
        error = 1
    except digitalocean.baseapi.JSONReadError as e:
        log.error(f'Could not parse json: {e}.')
        error = 1
    except digitalocean.baseapi.NotFoundError as e:
        log.error(f'Ressource not found: {e}.')
        error = 1
    except Exception as e:
        log.error(f'Unexpected exception: {e}.')
        error = 1


def _prune_volume_snapshots(volume: digitalocean.Volume,
                            retention: int) -> None:
    """Prune goutte snapshots if tmore than the configured retention time"""
    global error
    try:
        all_snapshots = _order_snapshots(volume.get_snapshots())
        snapshots = [snapshot for snapshot in all_snapshots
                     if snapshot.name[:6] == 'goutte']
        if len(snapshots) > retention:
            log.debug(f'{volume.name} - Exceed retention policy by '
                      f'{len(snapshots) - retention}')
            for snapshot in snapshots[:len(snapshots)-retention]:
                log.info(f'{volume.name} - Prune ({snapshot.name})')
                snapshot.destroy()
    except digitalocean.baseapi.TokenError as e:
        log.error(f'Token not valid: {e}.')
        error = 1
    except digitalocean.baseapi.DataReadError as e:
        log.error(f'Could not read response: {e}.')
        error = 1
    except digitalocean.baseapi.JSONReadError as e:
        log.error(f'Could not parse json: {e}.')
        error = 1
    except digitalocean.baseapi.NotFoundError as e:
        log.error(f'Ressource not found: {e}.')
        error = 1
    except Exception as e:
        log.error(f'Unexpected exception: {e}.')
        error = 1


def _order_snapshots(snapshots: List[digitalocean.Snapshot]
                     ) -> List[digitalocean.Snapshot]:
    """Order snapshots by creation date"""
    return sorted(snapshots, key=lambda x: x.created_at)
