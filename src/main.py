import asyncio
import logging

import pymongo

from core.interfaces.scraper import IScraper
from core.interfaces.vacancy_notifier import IVacancyNotifier
from env.env_vars import env
from log.logging import setup_logging
from services.mongo_vacancy_repository.repository import MongoVacancyRepository
from services.notifiers.telegram_notifier import TelegramNotifier
from services.notifiers.telegram_notifier_verbose import TelegramNotifierVerbose
from services.scraper_notifier_orchestrator.orchestrator import ScraperNotifierOrchestrator
from services.scrapers.dummy.scraper import DummyScraper
from services.scrapers.habr.scraper import HabrScraper
from services.scrapers.headhunter.scraper import HeadHunterScraper
from utils.telegram_sender import TelegramSender

logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logging()
    repository = MongoVacancyRepository(pymongo.AsyncMongoClient(env.mongodb_url.encoded_string()).get_default_database())

    scrapers: list[IScraper] = [
        HabrScraper(repository),
        HeadHunterScraper(repository),
        # DummyScraper(repository),
    ]

    notifiers: list[IVacancyNotifier] = [
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

    o = ScraperNotifierOrchestrator(scrapers, notifiers, repository)

    while True:
        logger.info("Started scraping...")
        await o.scrape_and_notify()
        await asyncio.sleep(3600.0)


if __name__ == "__main__":
    asyncio.run(main())
