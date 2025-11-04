from abc import ABC, abstractmethod

from core.types.vacancy import Vacancy


class IVacancyNotifier(ABC):
    @abstractmethod
    async def notify(self, vacancies: list[Vacancy]) -> None:
        raise NotImplementedError
