import asyncio
import logging
from collections.abc import Callable

from aiokafka import AIOKafkaProducer

from src.core.interfaces.scraper import IScraper
from src.core.interfaces.vacancy_notifier import IVacancyNotifier
from src.core.interfaces.vacancy_repository import IVacancyRepository
from src.env.habr_scraper_env import HabrScraperEnvironSettings
from src.env.hh_scraper_env import HeadHunterScraperEnvironSettings
from src.env.kafka_notifier_env import KafkaNotfierEnvironSettings
from src.env.tg_notifier_env import TelegramNotfierEnvironSettings
from src.env.tg_verbose_notifier_env import TelegramVerboseNotfierEnvironSettings
from src.services.notifiers.kafka_notifier import KafkaNotifier
from src.services.notifiers.telegram_notifier import TelegramNotifier
from src.services.notifiers.telegram_notifier_verbose import TelegramNotifierVerbose
from src.services.scraper_notifier_orchestrator.orchestrator import ScraperNotifierOrchestrator
from src.services.scrapers.habr.scraper import HabrScraper
from src.services.scrapers.headhunter.scraper import HeadHunterScraper
from src.utils.telegram_sender import TelegramSender

_logger = logging.getLogger(__name__)


async def _kafka_notifier_builder() -> KafkaNotifier:
    producer = AIOKafkaProducer(
        bootstrap_servers=KafkaNotfierEnvironSettings().servers,  # type: ignore
        request_timeout_ms=20000,
    )
    await producer.start()
    return KafkaNotifier(producer)


NOTIFIER_REGISTRY: dict[str, Callable[[], IVacancyNotifier]] = {
    "TELEGRAM": lambda: TelegramNotifier(
        TelegramSender(TelegramNotfierEnvironSettings().token, TelegramNotfierEnvironSettings().chat),  # type: ignore
    ),
    "TELEGRAM_VERBOSE": lambda: TelegramNotifierVerbose(
        TelegramSender(TelegramVerboseNotfierEnvironSettings().token, TelegramVerboseNotfierEnvironSettings().chat),  # type: ignore
    ),
    "KAFKA": _kafka_notifier_builder,  # type: ignore
}

SCRAPER_REGISTRY: dict[str, Callable[[IVacancyRepository], IScraper]] = {
    "HH": lambda repo: HeadHunterScraper(repo, HeadHunterScraperEnvironSettings().urls),  # type: ignore
    "HABR": lambda repo: HabrScraper(repo, HabrScraperEnvironSettings().urls),  # type: ignore
}


async def build_orchestrator(
    repository: IVacancyRepository,
    enabled_scrapers: list[str],
    enabled_notifiers: list[str],
) -> ScraperNotifierOrchestrator:
    notifiers: list[IVacancyNotifier] = []
    scrapers: list[IScraper] = []

    for scraper_name in enabled_notifiers:
        if scraper_name not in NOTIFIER_REGISTRY:
            raise ValueError(scraper_name + " not in NOTIFIER_REGISTRY")

        _logger.info(f"Enabled {scraper_name}")
        factory = NOTIFIER_REGISTRY[scraper_name]()

        if asyncio.iscoroutine(factory):
            notifiers.append(await factory)
            continue

        notifiers.append(factory)

    for scraper_name in enabled_scrapers:
        if scraper_name not in SCRAPER_REGISTRY:
            raise ValueError(scraper_name + " not in SCRAPER_REGISTRY")

        factory = SCRAPER_REGISTRY[scraper_name](repository)

        if asyncio.iscoroutine(factory):
            scrapers.append(await factory)
            continue

        scrapers.append(factory)

    return ScraperNotifierOrchestrator(scrapers, notifiers, repository)
