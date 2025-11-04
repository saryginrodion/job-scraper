import logging
from http import HTTPStatus
from typing import Any, override

from httpx import AsyncClient

from core.errors.scraper import ScraperFetchError
from core.interfaces.vacancy_repository import IVacancyRepository
from core.types.vacancy import Vacancy
from services.scrapers.BaseScraper import BaseScraper
from utils.retry import async_retry

logger = logging.getLogger(__name__)


class HabrScraper(BaseScraper):
    BASE_URL = "https://career.habr.com"
    SCRAPING_URLS = [
        "/api/frontend/vacancies?q=Python&sort=relevance&type=all&currency=RUR&s[]=2&s[]=4&s[]=82&s[]=7&s[]=84&s[]=73&s[]=85&s[]=72",
        "/api/frontend/vacancies?q=FastAPI&sort=relevance&type=all&currency=RUR&s[]=2&s[]=4&s[]=82&s[]=7&s[]=84&s[]=73&s[]=85&s[]=72",
        "/api/frontend/vacancies?sort=relevance&type=all&skills[]=1349&remote=true&currency=RUR&s[]=2&s[]=3&s[]=4&s[]=82&s[]=72&s[]=5&s[]=75&s[]=6&s[]=1&s[]=77&s[]=7&s[]=83&s[]=84&s[]=73&s[]=8&s[]=85&s[]=86&s[]=188&s[]=178&s[]=106",
    ]

    def __init__(self, repository: IVacancyRepository) -> None:
        super().__init__(logger, repository)

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
            for endpoint in self.SCRAPING_URLS
        ]
