import sys
from typing import List
from typing import Set
from typing import Union

import colorlog
import digitalocean
from digitalocean.baseapi import DataReadError
from digitalocean.baseapi import EndPointError
from digitalocean.baseapi import Error
from digitalocean.baseapi import JSONReadError
from digitalocean.baseapi import NotFoundError
from digitalocean.baseapi import TokenError

log = colorlog.getLogger(__name__)


class DigitalOcean:
    def __init__(self, token: str) -> None:
        self.manager = digitalocean.Manager(token=token)
        log.debug("created digitalocean manager")

    def __repr__(self) -> str:
        return f'DigitalOcean("{self.manager.token}")'

    def get_droplets(
        self, names: List[str], tags: List[str], unique: bool = True
    ) -> Union[List[digitalocean.Droplet], Set[digitalocean.Droplet]]:
        droplets = list()
        all_droplets = self._get_all_droplets()
        droplets.extend([droplet for droplet in all_droplets if droplet.name in names])
        for tag in tags:
            droplets.extend(
                [droplet for droplet in all_droplets if tag in droplet.tags]
            )
        return set(droplets) if unique else droplets

    def get_volumes(
        self, names: List[str], unique: bool = True
    ) -> Union[List[digitalocean.Volume], Set[digitalocean.Volume]]:
        volumes = list()
        all_volumes = self._get_all_volumes()
        volumes.extend([volume for volume in all_volumes if volume.name in names])
        return set(volumes) if unique else volumes

    def _get_all_droplets(self) -> List[digitalocean.Droplet]:
        try:
            droplets = self.manager.get_all_droplets()
        except (DataReadError, JSONReadError, EndPointError, NotFoundError):
            log.fatal("api error while trying to fetch droplets")
            sys.exit(1)
        except (TokenError):
            log.fatal("invalid digitalocean api token")
            sys.exit(1)
        except (Error):
            log.fatal("unexpected api error while trying to fetch volumes")
            sys.exit(1)
        return droplets

    def _get_all_volumes(self) -> List[digitalocean.Volume]:
        try:
            volumes = self.manager.get_all_volumes()
        except (DataReadError, JSONReadError, EndPointError):
            log.fatal("api error while trying to fetch volumes")
            sys.exit(1)
        except (TokenError):
            log.fatal("invalid digitalocean api token")
            sys.exit(1)
        except (Error):
            log.fatal("unexpected api error while trying to fetch volumes")
            sys.exit(1)
        return volumes
