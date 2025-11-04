from pymongo.asynchronous.database import AsyncDatabase

from src.core.interfaces.vacancy_repository import IVacancyRepository
from src.core.types.vacancy import Vacancy
from src.services.mongo_vacancy_repository.dto import VacancyDTO


class MongoVacancyRepository(IVacancyRepository):
    COLLECTION_NAME = "vacancies"

    def __init__(self, db: AsyncDatabase) -> None:
        self._db = db
        self._collection = self._db[self.COLLECTION_NAME]

    async def save_vacancies(self, vacancies: list[Vacancy]) -> None:
        vacancies_docs = [VacancyDTO.from_vacancy(v).model_dump() for v in vacancies]
        await self._collection.insert_many(vacancies_docs)

    async def by_source_vacancy_id(self, scraper_name: str, source_vacancy_id: str) -> Vacancy | None:
        vacancy_doc = await self._collection.find_one({"scraper_name": scraper_name, "source_id": source_vacancy_id})

        if not vacancy_doc:
            return None

        return VacancyDTO(**vacancy_doc).to_vacancy()
