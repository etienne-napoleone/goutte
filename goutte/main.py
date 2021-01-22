import click
import colorlog

from goutte import config
from goutte import __version__

log = colorlog.getLogger(__name__)


@click.command(help="DigitalOcean snapshot automation")
@click.argument("do_token", envvar="GOUTTE_DO_TOKEN")
@click.option(
    "--config",
    "config_path",
    envvar="GOUTTE_CONFIG_PATH",
    type=click.Path(dir_okay=False, allow_dash=True),
    default="goutte.yml",
    help="Path to",
)
@click.option(
    "--debug", envvar="GOUTTE_DEBUG", is_flag=True, help="Enable debug logging."
)
@click.version_option(version=__version__)
def entrypoint(config_path: str, do_token: str, debug: bool) -> None:
    log.info(f"goutte, version {__version__}")
    if debug:
        colorlog.getLogger().setLevel("DEBUG")
        log.debug("running with debug logging")
    config.get(config_path)
