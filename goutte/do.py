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
        """Class for DigitalOcean interactions

        Args:
            token (str): Digitalocean api token.
        """
        self.manager = digitalocean.Manager(token=token)
        log.debug("created digitalocean manager")

    def __repr__(self) -> str:
        return f'DigitalOcean("{self.manager.token}")'

    def get_droplets(
        self, names: List[str], tags: List[str], unique: bool = True
    ) -> Union[List[digitalocean.Droplet], Set[digitalocean.Droplet]]:
        """Get droplets to snapshot

        Args:
            names (List[str]): List of droplet names to filter in.
            tags (List[str]): List of droplet tags to filter in.
            unique (bool, optional): Transform the list to a set. Defaults to True.

        Returns:
            Union[List[digitalocean.Droplet], Set[digitalocean.Droplet]]: Droplets.
        """
        droplets = list()
        all_droplets = self._get_all_droplets()
        for name in names:
            matches = [droplet for droplet in all_droplets if name == droplet.name]
            if matches:
                log.debug(f'found {len(matches)} match for droplet name "{name}"')
                droplets.extend(matches)
            else:
                log.warning(f'no match found for droplet name "{name}"')
        for tag in tags:
            matches = [droplet for droplet in all_droplets if tag in droplet.tags]
            if matches:
                log.debug(f'found {len(matches)} match for droplet tag "{tag}"')
                droplets.extend(matches)
            else:
                log.warning(f'no match found for droplet tag "{tag}"')
        return set(droplets) if unique else droplets

    def get_volumes(
        self, names: List[str], unique: bool = True
    ) -> Union[List[digitalocean.Volume], Set[digitalocean.Volume]]:
        """Get volumes to snapshot

        Args:
            names (List[str]): List of volume names to filter in.
            unique (bool, optional): Transform the list to a set. Defaults to True.

        Returns:
            Union[List[digitalocean.Volume], Set[digitalocean.Volume]]: Volumes.
        """
        volumes = list()
        all_volumes = self._get_all_volumes()
        for name in names:
            matches = [volume for volume in all_volumes if name == volume.name]
            if matches:
                log.debug(f'found {len(matches)} match for volume name "{name}"')
                volumes.extend(matches)
            else:
                log.warning(f'no match found for volume name "{name}"')
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
