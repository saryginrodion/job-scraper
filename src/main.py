import asyncio
import logging

import pymongo

from src.config.scraper_notifier_orchestrator_builder import build_orchestrator
from src.env.env_vars import env
from src.log.logging import setup_logging
from src.services.mongo_vacancy_repository.repository import MongoVacancyRepository

logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logging()

    repository = MongoVacancyRepository(pymongo.AsyncMongoClient(env.mongodb_url.encoded_string()).get_default_database())
    scraper_notifier_orchestrator = await build_orchestrator(repository, env.scrapers, env.notifiers)
    await scraper_notifier_orchestrator.scrape_and_notify()
    await scraper_notifier_orchestrator.aclose()


if __name__ == "__main__":
    event_loop = asyncio.get_event_loop()
    if event_loop.is_running():
        asyncio.create_task(main())
    else:
        event_loop.run_until_complete(main())
