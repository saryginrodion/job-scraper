import http
import logging
from typing import Literal

import httpx
from pydantic import BaseModel

from src.utils.retry import async_retry

logger = logging.getLogger(__name__)


class TelegramSenderError(Exception):
    def __init__(self, status_code: int, *args: object) -> None:
        super().__init__(*args)
        self.status_code = status_code


class SendMessageOpts(BaseModel):
    parse_mode: Literal["MarkdownV2", "Markdown", "HTML"] = "MarkdownV2"


_default_send_message_opts = SendMessageOpts()

class TelegramSender:
    API_BASE = "https://api.telegram.org"

    def __init__(self, token: str, chat_id: str) -> None:
        self._token = token
        self._api_bot_base = self.API_BASE + "/bot" + self._token
        self._chat_id = chat_id


    @async_retry(retries=3, delay_func=lambda ctx: ctx.retry_attempt * 30)
    async def send_message(self, text: str, opts: SendMessageOpts = _default_send_message_opts) -> None:
        logger.debug(text)

        async with httpx.AsyncClient() as c:
            resp = await c.post(
                self._api_bot_base + "/sendMessage",
                json={
                    "chat_id": self._chat_id,
                    "text": text,
                    "parse_mode": opts.parse_mode,
                },
            )

            if resp.status_code != http.HTTPStatus.OK:
                logger.info(f"Failed to send telegram messsage. Code: {resp.status_code}. Body: {resp.json()}")
                raise TelegramSenderError(resp.status_code, f"Failed to send telegram messsage. Code: {resp.status_code}. Body: {resp.json()}")
