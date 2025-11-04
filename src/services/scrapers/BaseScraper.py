import asyncio
import logging
from abc import abstractmethod
from collections.abc import Iterator
from typing import override

from httpx import AsyncClient

from core.interfaces.scraper import IScraper
from core.interfaces.vacancy_repository import IVacancyRepository
from core.types.vacancy import Vacancy
from utils.exception_suppress import async_exception_suppress


class BaseScraper(IScraper):
    def __init__(self, logger: logging.Logger, repository: IVacancyRepository) -> None:
        self._repository = repository
        self._logger = logger

    @override
    async def fetch_new_vacancies(self) -> list[Vacancy]:
        vacancies: list[Vacancy] = []

        coroutines = [
            async_exception_suppress(Exception, logger=self._logger, loglevel=logging.WARNING, default=[])(self.fetch_pages_from_endpoint)(url)
            for url in self.endpoints()
        ]

        fetched_vacancies: list[list[Vacancy]] = await asyncio.gather(*coroutines)  # type: ignore

        for vacancy_list in fetched_vacancies:
            vacancies.extend(vacancy_list)

        return vacancies


    async def fetch_pages_from_endpoint(self, endpoint: str) -> list[Vacancy]:
        vacancies = []

        pages = self.page_number_generator()
        while True:
            # TODO: it can be None?
            page = next(pages)

            fetched_vacancies: list[Vacancy] = await async_exception_suppress(
                Exception,
                logger=self._logger,
                loglevel=logging.WARNING,
                default=[],
            )(self.fetch_vacancies)(endpoint, page)  # type: ignore

            extend_list: list[Vacancy] = []

            for vacancy in fetched_vacancies:
                if await self.is_already_exists(vacancy.source_id):
                    continue

                extend_list.append(vacancy)

            if len(extend_list) == 0:
                break

            vacancies.extend(extend_list)

        return vacancies

    @override
    async def is_already_exists(self, source_vacancy_id: str) -> bool:
        return await self._repository.by_source_vacancy_id(self.__class__.__name__, source_vacancy_id) is not None

    @abstractmethod
    async def fetch_vacancies(self, url: str, page: int) -> list[Vacancy]:
        pass

    @abstractmethod
    def endpoints(self) -> list[str]:
        pass

    @classmethod
    def page_number_generator(cls) -> Iterator[int]:
        yield from range(1, 1000)
