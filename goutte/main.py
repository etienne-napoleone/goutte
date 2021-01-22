from goutte import config


def entrypoint() -> None:
    config.get("goutte.yml")
