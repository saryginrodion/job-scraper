import logging  # noqa: I001

from celery import Celery

from src.env.env_vars import env
from src.log.logging import setup_logging

logger = logging.getLogger(__name__)

setup_logging()
app = Celery("tasks", broker=env.celery_broker_url, backend=env.celery_backend_url)

app.autodiscover_tasks(["src.celery.tasks.orchestrator_tasks"])

app.conf.beat_schedule = {
    "scrape-and-notify-15m": {
        "task": "orchestrator.scrape_and_notify",
        "schedule": 15 * 60,
        "args": (),
    },
}
