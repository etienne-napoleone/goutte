import colorlog

__version__ = "2.0.0"

handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(yellow)s%(asctime)s%(reset)s - %(log_color)s%(levelname)s%(reset)s"
        " - %(message)s",
        "%H:%M:%S",
    )
)
logger = colorlog.getLogger()
logger.setLevel("INFO")
logger.addHandler(handler)
