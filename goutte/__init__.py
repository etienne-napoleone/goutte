import colorlog

__version__ = '1.0.1'

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(yellow)s%(asctime)s%(reset)s - %(log_color)s%(levelname)s%(reset)s'
    ' - %(message)s',
    '%H:%M:%S'
))
logger = colorlog.getLogger(__name__)
logger.setLevel('INFO')
logger.addHandler(handler)
