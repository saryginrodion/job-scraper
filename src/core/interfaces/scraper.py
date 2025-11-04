from abc import ABC, abstractmethod

from src.core.types.vacancy import Vacancy


class IScraper(ABC):
    @abstractmethod
    async def fetch_new_vacancies(self) -> list[Vacancy]:
        raise NotImplementedError


    @abstractmethod
    async def is_already_exists(self, source_vacancy_id: str) -> bool:
        raise NotImplementedError
