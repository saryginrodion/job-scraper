import logging
from typing import Annotated

from kafka.admin import NewTopic
from kafka.admin.client import KafkaAdminClient
from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode

logger = logging.getLogger(__name__)
logger.setLevel("INFO")


class EnvironSettings(BaseSettings):
    kafka_servers: Annotated[list[str], NoDecode]

    @field_validator("kafka_servers", mode="before")
    @classmethod
    def decode_numbers(cls, v: str) -> list[str]:
        return v.split(",")


def main():
    env = EnvironSettings()  # type: ignore

    try:
        admin = KafkaAdminClient(bootstrap_servers=env.kafka_servers, client_id="kafka_setup")
        logger.info("Starting kafka setup")

        resp = admin.create_topics(
            new_topics=[
                NewTopic(
                    name="vacancies.new",
                    num_partitions=1,
                    replication_factor=1,
                ),
            ],
        )

        logger.info(f"Topic creation response: {resp}")
    except Exception as e:  # noqa: BLE001
        logger.fatal(f"Failed to setup kafka. Exception: {e}")


if __name__ == "__main__":
    main()
