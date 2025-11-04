from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass
class Vacancy:
    name: str
    details: str
    source_id: str
    source_url: str
    scraper_name: str
    additional_data: Any

    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now())
