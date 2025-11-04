# Job scraper
Scrapes jobs from career.habr.com, hh.ru. _(maybe more in future)_

# Architecture
## Scrapers
Scrapers parsing `src.core.types.vacancy.Vacancy` objects from websites.
All scrapers is based on `src.core.interfaces.scraper.IScraper` class

You can watch examples of scrapers in `src/services/scrapers` (They are using helper class `src.services.scrapers.BaseScraper.BaseScraper`)

## VacancyNotifiers
All scrapers is based on `src.core.interfaces.vacancy_notifier.IVacancyNotifier` class

# How to run
- Set up `.env` file in root directory of this repository (template: `.env.example`)
- Start redis + mongodb (if you saved defaults from `.env.example`, you can start them with `docker compose up --build`
- Start celery worker with `uv sync && uv run celery -A src.celery_app worker -B -E -l INFO`
- Start one time scraping task with `uv run -m src.main`
