import colorlog

__version__ = '0.1.0'

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(blue)s%(asctime)s%(reset)s - %(log_color)s%(levelname)s%(reset)s'
    ' - %(yellow)s%(name)s%(reset)s - %(message)s',
    '%H:%M:%S'
))
logger = colorlog.getLogger(__name__)
logger.setLevel('INFO')
logger.addHandler(handler)
