import logging

from env.env_vars import env
from log.telegram_handler import TelegramLoggingHandler
from utils.telegram_sender import TelegramSender

_loglevel_map = {
        "DEBUG": logging.DEBUG,
        "WARNING": logging.WARNING,
        "WARN": logging.WARNING,
        "INFO": logging.INFO,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
}

def str_to_loglevel(s: str) -> int:
    if s not in _loglevel_map:
        raise Exception("Can not convert string " + s + " to log level")  # noqa: TRY002

    return _loglevel_map[s]



def setup_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(str_to_loglevel(env.log_level))

    tg_handler = TelegramLoggingHandler(
        TelegramSender(env.log_tg_token, env.log_tg_chat),
        str_to_loglevel(env.log_tg_level),
    )

    console_fmt = "%(asctime)s [%(levelname)s] %(module)s:%(lineno)d:%(funcName)s - %(message)s"
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(console_fmt))

    logger.addHandler(tg_handler)
    logger.addHandler(console_handler)
