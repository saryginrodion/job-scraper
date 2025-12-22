import asyncio
import logging
from typing import override

from src.core.interfaces.async_closable import AsyncClosable
from src.core.interfaces.scraper import IScraper
from src.core.interfaces.vacancy_notifier import IVacancyNotifier
from src.core.interfaces.vacancy_repository import IVacancyRepository
from src.core.types.vacancy import Vacancy
from src.utils.exception_suppress import async_exception_suppress
from src.utils.remove_duplicates import remove_duplicates

logger = logging.getLogger(__name__)


class ScraperNotifierOrchestrator(AsyncClosable):
    def __init__(self, scrapers: list[IScraper], notifiers: list[IVacancyNotifier], vacancy_repostory: IVacancyRepository) -> None:
        self._scrapers = scrapers
        self._notifiers = notifiers
        self._repository = vacancy_repostory

    async def scrape(self) -> list[Vacancy]:
        logger.info("Started scraping...")
        vacancies: list[Vacancy] = []

        coroutines = [
            async_exception_suppress(Exception, logger=logger, default=[])(
                s.fetch_new_vacancies,
            )()
            for s in self._scrapers
        ]

        fetched_vacancies = await asyncio.gather(*coroutines)

        for vacancy_list in fetched_vacancies:
            vacancies.extend(vacancy_list)  # type: ignore

        vacancies_no_duplicates = list(remove_duplicates(vacancies, lambda x: x.source_id))

        logger.info(f"Scraped {len(vacancies_no_duplicates)} unique vacancies from {len(self._scrapers)} scrapers")
        return vacancies_no_duplicates

    async def notify(self, vacancies: list[Vacancy]) -> None:
        logger.info(f"Starting notifying about {len(vacancies)} vacancies")

        coroutines = [async_exception_suppress(Exception, logger=logger, loglevel=logging.WARNING)(n.notify)(vacancies) for n in self._notifiers]

        await asyncio.gather(*coroutines)

        logger.info("Notification ended")

    async def scrape_and_notify(self) -> None:
        try:
            vacancies = await self.scrape()
            if len(vacancies) == 0:
                logger.info("Scraped 0 vacancies!")
                return
            await self._repository.save_vacancies(vacancies)
            await self.notify(vacancies)

            logger.info("Ended scrape_and_notify")
        except Exception as e:
            logger.error(e)

    async def _close_scrapers(self) -> None:
        for scraper in self._scrapers:
            if isinstance(scraper, AsyncClosable):
                await scraper.aclose()

    async def _close_notifiers(self) -> None:
        for scraper in self._scrapers:
            if isinstance(scraper, AsyncClosable):
                await scraper.aclose()

    @override
    async def aclose(self) -> None:
        if isinstance(self._repository, AsyncClosable):
            await self._repository.aclose()

        await self._close_notifiers()
        await self._close_scrapers()
