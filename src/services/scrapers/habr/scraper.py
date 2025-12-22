import logging
from http import HTTPStatus
from typing import Any, override

from httpx import AsyncClient

from src.core.errors.scraper import ScraperFetchError
from src.core.interfaces.vacancy_repository import IVacancyRepository
from src.core.types.vacancy import Vacancy
from src.services.scrapers.BaseScraper import BaseScraper
from src.utils.retry import async_retry

logger = logging.getLogger(__name__)


class HabrScraper(BaseScraper):
    BASE_URL = "https://career.habr.com"

    def __init__(self, repository: IVacancyRepository, scraping_endpoints: list[str]) -> None:
        super().__init__(logger, repository)

        self.scraping_endpoints = scraping_endpoints
        self._client = AsyncClient()

    @override
    @async_retry(retries=3)
    async def fetch_vacancies(self, url: str, page: int) -> list[Vacancy]:
        url = url + f"&page={page}"

        logger.info("Fetching " + url)

        resp = await self._client.get(url)

        if resp.status_code != HTTPStatus.OK:
            logger.error("Failed to fetch. Code: " + str(resp.status_code) + ". Body text: " + resp.text)
            raise ScraperFetchError("HabrScraper: Failed to fetch.")

        resp_json: dict[str, Any] = resp.json()

        return [
            Vacancy(
                name=v["title"],
                details="Навыки: " + ", ".join([s["title"] for s in v["skills"]]),
                source_id=str(v["id"]),
                source_url=f"{self.BASE_URL}{v['href']}",
                scraper_name=self.__class__.__name__,
                additional_data={
                    "company": v["company"]["title"],
                    "remote": v["remoteWork"],
                    "published": v["publishedDate"]["title"],
                    "salary": v["salary"]["formatted"],
                },
            )
            for v in resp_json.get("list", [])
        ]


    @override
    def endpoints(self) -> list[str]:
        return [
            f"{self.BASE_URL}{endpoint}"
            for endpoint in self.scraping_endpoints
        ]
