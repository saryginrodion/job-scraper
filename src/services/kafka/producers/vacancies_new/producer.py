from src.services.kafka.base_producer import BaseProducer
from src.services.kafka.producers.vacancies_new.dto import VacanciesNewEventDTO


class NewVacancyProducer(BaseProducer[VacanciesNewEventDTO]):
    TOPIC_NAME = "vacancies.new"
