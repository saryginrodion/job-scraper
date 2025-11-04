import asyncio
import logging

import pymongo

from src.celery_app import app
from src.core.interfaces.scraper import IScraper
from src.core.interfaces.vacancy_notifier import IVacancyNotifier
from src.env.env_vars import env
from src.services.mongo_vacancy_repository.repository import MongoVacancyRepository
from src.services.notifiers.telegram_notifier import TelegramNotifier
from src.services.notifiers.telegram_notifier_verbose import TelegramNotifierVerbose
from src.services.scraper_notifier_orchestrator.orchestrator import ScraperNotifierOrchestrator
from src.services.scrapers.habr.scraper import HabrScraper
from src.services.scrapers.headhunter.scraper import HeadHunterScraper
from src.utils.telegram_sender import TelegramSender

logger = logging.getLogger(__name__)


def new_scraper_notifier_orchestrator() -> ScraperNotifierOrchestrator:
    _repository = MongoVacancyRepository(pymongo.AsyncMongoClient(env.mongodb_url.encoded_string()).get_default_database())

    _scrapers: list[IScraper] = [
        HabrScraper(_repository),
        HeadHunterScraper(_repository),
    ]

    _notifiers: list[IVacancyNotifier] = [
        TelegramNotifier(
            TelegramSender(
                env.tg_notifier_token,
                env.tg_notifier_chat,
            ),
        ),
        TelegramNotifierVerbose(
            TelegramSender(
                env.tg_notifier_token,
                env.tg_notifier_chat_verbose,
            ),
        ),
    ]

    return ScraperNotifierOrchestrator(_scrapers, _notifiers, _repository)


@app.task
def scrape_and_notify() -> None:
    async def async_task() -> None:
        scraper_notifier_orchestrator = new_scraper_notifier_orchestrator()
        await scraper_notifier_orchestrator.scrape_and_notify()

    coro = async_task()

    try:
        asyncio.create_task(coro)
    except:
        asyncio.run(coro)
