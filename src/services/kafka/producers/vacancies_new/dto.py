from pydantic import BaseModel

from src.dto.vacancy import VacancyDTO


class VacanciesNewEventDTO(BaseModel):
    vacancies: list[VacancyDTO]
