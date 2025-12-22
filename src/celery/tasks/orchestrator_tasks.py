import asyncio
import logging

import pymongo

from src.celery_app import app
from src.config.scraper_notifier_orchestrator_builder import build_orchestrator
from src.env.env_vars import env
from src.services.mongo_vacancy_repository.repository import MongoVacancyRepository

logger = logging.getLogger(__name__)


@app.task(name="orchestrator.scrape_and_notify")
def scrape_and_notify() -> None:
    async def async_task() -> None:
        repository = MongoVacancyRepository(pymongo.AsyncMongoClient(env.mongodb_url.encoded_string()).get_default_database())
        scraper_notifier_orchestrator = await build_orchestrator(repository, env.scrapers, env.notifiers)
        await scraper_notifier_orchestrator.scrape_and_notify()
        await scraper_notifier_orchestrator.aclose()

    coro = async_task()

    try:
        asyncio.create_task(coro)
    except:
        asyncio.run(coro)
