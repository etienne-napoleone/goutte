import click
import toml

from goutte import __version__


@click.command(help='DigitalOcean snapshot automation service')
@click.argument('config', envvar='GOUTTE_CONFIG', type=click.File('r'))
@click.argument('do_key', envvar='GOUTTE_DO_KEY')
@click.option('--oneshot', is_flag=True, help='Run all tasks and then stops')
@click.version_option(version=__version__)
def main(config: click.File, do_key: str, oneshot: bool) -> None:
    """Command line interface entrypoint"""
    print(toml.load(config))
