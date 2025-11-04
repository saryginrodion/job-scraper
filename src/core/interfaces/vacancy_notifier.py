from abc import ABC, abstractmethod

from src.core.types.vacancy import Vacancy


class IVacancyNotifier(ABC):
    @abstractmethod
    async def notify(self, vacancies: list[Vacancy]) -> None:
        raise NotImplementedError
