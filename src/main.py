import logging

from src.celery.tasks.orchestrator_tasks import scrape_and_notify
from src.log.logging import setup_logging

logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging()
    scrape_and_notify()


if __name__ == "__main__":
    main()
