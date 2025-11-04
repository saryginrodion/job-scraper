import asyncio
import logging
import traceback

from utils.telegram import escape_markdown_v2
from utils.telegram_sender import TelegramSender

_level_emoji_mapper = {
    logging.DEBUG: "🐛",
    logging.INFO: "ℹ️",  # noqa: RUF001
    logging.WARNING: "⚠️",
    logging.ERROR: "❌",
    logging.CRITICAL: "💥",
}


class TelegramLoggingHandler(logging.Handler):
    def __init__(self, telegram_sender: TelegramSender, level: int = 0) -> None:
        super().__init__(level)
        self._sender = telegram_sender

    def emit(self, record: logging.LogRecord) -> None:
        try:
            asyncio.create_task(self.async_emit(record))  # noqa: RUF006
        except:  # noqa: E722
            asyncio.run(self.async_emit(record))

    async def async_emit(self, record: logging.LogRecord) -> None:
        try:
            await self._sender.send_message(
                text=f"""{_level_emoji_mapper.get(record.levelno, "?")} {record.levelname}

*time*: {escape_markdown_v2(record.asctime)}
*name*: {escape_markdown_v2(record.name)}
*module:lineno:funcname*: {escape_markdown_v2(record.module)}:{escape_markdown_v2(str(record.lineno))}:{escape_markdown_v2(record.funcName)}
*message*: {escape_markdown_v2(record.message)}""",
            )
        except:  # noqa: E722
            traceback.print_exc()
