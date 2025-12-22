import logging
from typing import override

from aiokafka import AIOKafkaProducer

from src.core.interfaces.async_closable import AsyncClosable
from src.core.interfaces.vacancy_notifier import IVacancyNotifier
from src.core.types.vacancy import Vacancy
from src.dto.vacancy import VacancyDTO
from src.services.kafka.producers.vacancies_new.dto import VacanciesNewEventDTO
from src.services.kafka.producers.vacancies_new.producer import NewVacancyProducer

logger = logging.getLogger(__name__)

class KafkaNotifier(IVacancyNotifier, AsyncClosable):
    def __init__(self, producer: AIOKafkaProducer) -> None:
        self._producer = NewVacancyProducer(producer)

    @override
    async def notify(self, vacancies: list[Vacancy]) -> None:
        event = VacanciesNewEventDTO(vacancies=[VacancyDTO.from_vacancy(v) for v in vacancies])
        await self._producer.send(event)

    @override
    async def aclose(self) -> None:
        await self._producer.aclose()
