import colorlog

__version__ = '0.1.0'

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s %(levelname)s -- %(message)s'))
logger = colorlog.getLogger(__name__)
logger.setLevel('INFO')
logger.addHandler(handler)
