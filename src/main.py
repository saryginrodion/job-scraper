import asyncio
import logging

import pymongo
from aiokafka import AIOKafkaProducer

from src.core.interfaces.scraper import IScraper
from src.core.interfaces.vacancy_notifier import IVacancyNotifier
from src.env.env_vars import env
from src.log.logging import setup_logging
from src.services.mongo_vacancy_repository.repository import MongoVacancyRepository
from src.services.notifiers.kafka_notifier import KafkaNotifier
from src.services.scraper_notifier_orchestrator.orchestrator import ScraperNotifierOrchestrator
from src.services.scrapers.dummy.scraper import DummyScraper

logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logging()
    _repository = MongoVacancyRepository(pymongo.AsyncMongoClient(env.mongodb_url.encoded_string()).get_default_database())

    _scrapers: list[IScraper] = [DummyScraper(_repository)]
    kafka_producer = AIOKafkaProducer(
        bootstrap_servers=env.kafka_servers,  # type: ignore
        request_timeout_ms=20000,
    )

    _notifiers: list[IVacancyNotifier] = [KafkaNotifier(kafka_producer)]
    orchestrator = ScraperNotifierOrchestrator(_scrapers, _notifiers, _repository)

    await kafka_producer.start()
    await orchestrator.scrape_and_notify()
    await kafka_producer.stop()

if __name__ == "__main__":
    event_loop = asyncio.get_event_loop()
    if event_loop.is_running():
        event_loop.run_until_complete(main())
    asyncio.run(main())
