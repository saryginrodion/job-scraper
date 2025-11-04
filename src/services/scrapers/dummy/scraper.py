import logging
from typing import override
from uuid import uuid4

from httpx import AsyncClient

from src.core.interfaces.vacancy_repository import IVacancyRepository
from src.core.types.vacancy import Vacancy
from src.services.scrapers.BaseScraper import BaseScraper
from src.utils.retry import async_retry

logger = logging.getLogger(__name__)


class DummyScraper(BaseScraper):
    def __init__(self, repository: IVacancyRepository) -> None:
        super().__init__(logger, repository)

        self._client = AsyncClient()

    @override
    @async_retry(retries=3)
    async def fetch_vacancies(self, url: str, page: int) -> list[Vacancy]:
        if page >= 3:
            return []

        return [
            Vacancy(
                name="Dummy " + str(i),
                details="Dummy details",
                source_id=str(uuid4()),
                source_url=f"https://example.com",
                scraper_name=self.__class__.__name__,
                additional_data={
                    "ok": True,
                },
            )
            for i in range(5)
        ]


    @override
    def endpoints(self) -> list[str]:
        return [
            "aioai",
        ]
