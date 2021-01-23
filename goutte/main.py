import click
import colorlog

from goutte import config
from goutte import utils
from goutte import __version__
from goutte.do import DigitalOcean

LABEL = "{name}-{type}-{item}-{date}.{id}.goutte"
DATE = utils.get_date()
ID = utils.get_id()

log = colorlog.getLogger(__name__)


@click.command(help="DigitalOcean snapshot automation")
@click.argument("do_token", envvar="GOUTTE_DO_TOKEN")
@click.option(
    "--config",
    "config_path",
    envvar="GOUTTE_CONFIG_PATH",
    type=click.Path(dir_okay=False, allow_dash=True),
    default="goutte.yml",
    help="Configuration file path.",
)
@click.option("--debug", envvar="GOUTTE_DEBUG", is_flag=True, help="Enable debug logs.")
@click.version_option(version=__version__)
def entrypoint(config_path: str, do_token: str, debug: bool) -> None:
    """CLI entrypoint

    Args:
        config_path (str): Configuration file path.
        do_token (str): DigitalOcean api token.
        debug (bool): Enable debug logs.
    """
    log.info(f"goutte, version {__version__}")
    if debug:
        colorlog.getLogger().setLevel("DEBUG")
        log.debug("running with debug logging")
    c = config.get(config_path)
    droplet_config = c["targets"].get("droplets", {})
    volume_config = c["targets"].get("volumes", {})
    do = DigitalOcean(token=do_token)
    droplets = do.get_droplets(
        names=droplet_config.get("names", []),
        tags=droplet_config.get("tags", []),
    )
    volumes = do.get_volumes(names=volume_config.get("names", []))
    log.info(
        f"found {len(droplets)} droplet(s) and {len(volumes)} volume(s) to snapshot"
    )
    for droplet in droplets:
        do.snapshot(
            droplet,
            LABEL.format(
                name=c["name"],
                type="droplet",
                item=droplet.name,
                id=ID,
                date=DATE,
            ),
        )
    for volume in volumes:
        volume.snapshot(
            volume,
            LABEL.format(
                name=c["name"],
                type="volume",
                item=droplet.name,
                id=ID,
                date=DATE,
            ),
        )
    log.info("done, bye!")
