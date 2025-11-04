import asyncio
import logging

from src.core.interfaces.scraper import IScraper
from src.core.interfaces.vacancy_notifier import IVacancyNotifier
from src.env.env_vars import env
from src.log.logging import setup_logging
from src.services.mongo_vacancy_repository.repository import MongoVacancyRepository
from src.services.notifiers.telegram_notifier import TelegramNotifier
from src.services.notifiers.telegram_notifier_verbose import TelegramNotifierVerbose
from src.services.scraper_notifier_orchestrator.orchestrator import ScraperNotifierOrchestrator
from src.services.scrapers.dummy.scraper import DummyScraper
from src.services.scrapers.habr.scraper import HabrScraper
from src.services.scrapers.headhunter.scraper import HeadHunterScraper
from src.utils.telegram_sender import TelegramSender

logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging()


if __name__ == "__main__":
    main()
