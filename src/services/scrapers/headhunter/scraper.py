import json
import logging
from http import HTTPStatus
from typing import override

import httpx
from bs4 import BeautifulSoup

from src.core.errors.scraper import ScraperFetchError
from src.core.interfaces.vacancy_repository import IVacancyRepository
from src.core.types.vacancy import Vacancy
from src.services.scrapers.BaseScraper import BaseScraper
from src.utils.retry import async_retry

logger = logging.getLogger(__name__)


class HeadHunterScraper(BaseScraper):
    BASE_URL = "https://hh.ru"

    SCRAPING_URLS = [
        # 1–3 years, Python FastAPI, remote
        "/search/vacancy?items_on_page=100&L_save_area=true&hhtmFrom=vacancy_search_filter&experience=between1And3&search_field=name&search_field=company_name&search_field=description&work_format=REMOTE&text=Python+FastAPI&enable_snippets=false",

        # 3–6 years, FastAPI, remote
        "/search/vacancy?ored_clusters=true&items_on_page=100&hhtmFrom=vacancy_search_list&hhtmFromLabel=vacancy_search_line&experience=between3And6&search_field=name&search_field=company_name&search_field=description&work_format=REMOTE&text=FastAPI&enable_snippets=false",
    ]

    HEADERS = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru,en;q=0.9",
        "Referer": "https://hh.ru/",
    }

    COOKIES = {
        "region": "113",  # Russia (prevents location selector redirect)
        "HH-Locale": "RU",
    }

    def __init__(self, repository: IVacancyRepository) -> None:
        super().__init__(logger, repository)

        self._client = httpx.AsyncClient(
            headers=self.HEADERS,
            cookies=self.COOKIES,
            timeout=25,
            follow_redirects=True,
        )

    @override
    def endpoints(self) -> list[str]:
        return [f"{self.BASE_URL}{endpoint}" for endpoint in self.SCRAPING_URLS]

    def _extract_initial_state(self, html: str) -> dict | None:
        soup = BeautifulSoup(html, "html.parser")

        template = soup.find("template", {"id": "HH-Lux-InitialState"})
        if not template:
            logger.error("HH-Lux-InitialState <template> not found")
            return None

        raw_json = template.string
        if not raw_json:
            logger.error("HH-Lux-InitialState template is empty")
            return None

        try:
            return json.loads(raw_json)
        except Exception as e:
            logger.error(f"Failed to parse HH-Lux-InitialState JSON: {e}")
            return None

    @override
    @async_retry(retries=3)
    async def fetch_vacancies(self, url: str, page: int) -> list[Vacancy]:
        full_url = f"{url}&page={page - 1}"

        if page - 1 == 0:
            full_url = f"{url}"

        logger.info(f"Fetching HH: {full_url}")

        resp = await self._client.get(full_url)

        if resp.status_code != HTTPStatus.OK:
            logger.error(f"HH fetch failed: {resp.status_code}")
            raise ScraperFetchError("HhScraper: Failed to fetch.")

        # Extract the JSON initial state
        state = self._extract_initial_state(resp.text)
        if not state:
            logger.warning("HH: no initial JSON state found → possible bot protection")
            return []

        vacancy_result = state.get("vacancySearchResult", {})
        vacancies = vacancy_result.get("vacancies", [])

        logger.info(f"HH: found {len(vacancies)} vacancies")

        results: list[Vacancy] = []

        for v in vacancies:
            try:
                vid = v.get("vacancyId")
                if not vid:
                    continue

                name = v.get("name", "Без названия")

                company = v.get("company", {}).get("visibleName") or v.get("company", {}).get("name") or "N/A"

                # Salary information is deeply nested
                compensation = v.get("compensation", {})
                salary = "Не указана"
                if "noCompensation" not in compensation:
                    # Sometimes compensation["compensation"]["value"]
                    salary = json.dumps(compensation, ensure_ascii=False)

                # Publication time
                published = v.get("publicationTime", {}).get("$") or "N/A"

                # Skills / requirements from snippet not available here
                # HH only provides them on vacancy page or in another API
                skills = []

                # Remote?
                work_formats = v.get("workFormats", [{}])
                remote = False
                try:
                    elements = work_formats[0].get("workFormatsElement", [])
                    remote = "REMOTE" in elements
                except Exception:
                    pass

                # URL to vacancy
                link = v.get("links", {}).get("desktop") or f"{self.BASE_URL}/vacancy/{vid}"

                results.append(
                    Vacancy(
                        name=name,
                        details="Навыки: " + ", ".join(skills),
                        source_id=str(vid),
                        source_url=link,
                        scraper_name=self.__class__.__name__,
                        additional_data={
                            "company": company,
                            "remote": remote,
                            "published": published,
                            "salary": salary,
                        },
                    )
                )

            except Exception as e:
                logger.error(f"Failed to parse vacancy block: {e}")

        return results
