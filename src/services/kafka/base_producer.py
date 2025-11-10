import logging

from aiokafka import AIOKafkaProducer
from pydantic import BaseModel

from src.utils.exception_suppress import async_exception_suppress
from src.utils.retry import async_retry

logger = logging.getLogger(__name__)


class BaseProducer[T: BaseModel]:
    TOPIC_NAME: str | None = None

    def __init__(self, producer: AIOKafkaProducer) -> None:
        self._producer = producer

    @property
    def topic_name(self) -> str:
        if self.TOPIC_NAME is None:
            raise NotImplementedError("TOPIC_NAME is null. Override it in subclasses")

        return self.TOPIC_NAME

    @async_retry(delay_func=lambda ctx: ctx.retry_attempt**2)
    async def send(self, event: T) -> None:
        try:
            await self._producer.send_and_wait(self.topic_name, bytes(event.model_dump_json(), encoding="utf-8"))
            logger.info(f"[{self.__class__.__name__}] Sent message to topic {self.topic_name}")
        except Exception as e:
            logger.warning(f"[{self.__class__.__name__}] Failed sending to topic {self.topic_name}. Exception: {e}")
            raise e
