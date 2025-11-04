from abc import ABC, abstractmethod

from core.types.vacancy import Vacancy


class IVacancyRepository(ABC):
    @abstractmethod
    async def save_vacancies(self, vacancies: list[Vacancy]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def by_source_vacancy_id(self, scraper_name: str, source_vacancy_id: str) -> Vacancy | None:
        raise NotImplementedError
