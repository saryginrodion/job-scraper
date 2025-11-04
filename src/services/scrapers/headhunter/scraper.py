import logging
from http import HTTPStatus
from typing import Any, override

from httpx import AsyncClient

from core.errors.scraper import ScraperFetchError
from core.interfaces.scraper import IScraper
from core.interfaces.vacancy_repository import IVacancyRepository
from core.types.vacancy import Vacancy
from utils.retry import async_retry

logger = logging.getLogger(__name__)


class HeadHunterScraper(IScraper):
    BASE_URL = "https://hh.ru"
    
    SCRAPING_URLS = [
        # 1 and 3, Python FastAPI, remote
        "/search/vacancy?items_on_page=100&L_save_area=true&hhtmFrom=vacancy_search_filter&experience=between1And3&search_field=name&search_field=company_name&search_field=description&work_format=REMOTE&text=Python+FastAPI&enable_snippets=false",

        # 3 and 6, FastAPI, remote
        "/search/vacancy?ored_clusters=true&items_on_page=100&hhtmFrom=vacancy_search_list&hhtmFromLabel=vacancy_search_line&experience=between3And6&search_field=name&search_field=company_name&search_field=description&work_format=REMOTE&text=FastAPI&enable_snippets=false",
    ]

    def __init__(self, repository: IVacancyRepository) -> None:
        self._client = AsyncClient()
        self._repository = repository

    @override
    async def fetch_new_vacancies(self) -> list[Vacancy]:
        vacancies = []

        for url in self.SCRAPING_URLS:
            fetched = await self._fetch_vacancies(self.BASE_URL + url)

            vacancies.extend([
                v
                for v in fetched
                if not await self.is_already_exists(v.source_id)
            ])

        return vacancies

    @override
    async def is_already_exists(self, source_vacancy_id: str) -> bool:
        return await self._repository.by_source_vacancy_id(self.__class__.__name__, source_vacancy_id) is not None

    @async_retry(retries=3)
    async def _fetch_vacancies(self, url: str) -> list[Vacancy]:
        logger.info("Fetching " + url)
        resp = await self._client.get(url)

        if resp.status_code != HTTPStatus.OK:
            logger.error("Failed to fetch. Code: " + str(resp.status_code) + ". Body text: " + resp.text)
            raise ScraperFetchError("HabrScraper: Failed to fetch.")

        return self._parse_vacancies(resp.content)


    async def _parse_vacancies(html: str) -> list[Vacancy]:
        pass
