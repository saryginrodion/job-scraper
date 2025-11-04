from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from src.core.types.vacancy import Vacancy


class VacancyDTO(BaseModel):
    id: str = Field(serialization_alias="_id")
    name: str
    details: str
    created_at: datetime
    source_id: str
    source_url: str
    scraper_name: str
    additional_data: Any

    @classmethod
    def from_vacancy(cls, vacancy: Vacancy) -> "VacancyDTO":
        return VacancyDTO(
            id=vacancy.id,
            name=vacancy.name,
            details=vacancy.details,
            created_at=vacancy.created_at,
            source_id=vacancy.source_id,
            source_url=vacancy.source_url,
            scraper_name=vacancy.scraper_name,
            additional_data=vacancy.additional_data,
        )

    def to_vacancy(self) -> Vacancy:
        return Vacancy(
            id=self.id,
            name=self.name,
            details=self.details,
            created_at=self.created_at,
            source_id=self.source_id,
            source_url=self.source_url,
            scraper_name=self.scraper_name,
            additional_data=self.additional_data,
        )
