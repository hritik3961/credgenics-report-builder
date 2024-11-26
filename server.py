import asyncio
from json import dumps, loads
import logging

from cg_kafka.consumer.JSONConsumer import JSONConsumer
from cg_kafka.producer.base import BaseProducer
from app.processing_report_ids import ReportUniqueIds
from database import init_database

from settings import APP_NAME, KAFKA_CONSUMER_AUTO_OFFSET_RESET, KAFKA_CONSUMER_CLIENT_ID, KAFKA_CONSUMER_DEFAULT_POLL_TIMEOUT_MS, KAFKA_CONSUMER_GROUP_ID, KAFKA_CONSUMER_MAX_POLL_RECORDS, KAFKA_CONSUMER_TOPIC_NAME, KAFKA_PRODUCER_CLIENT_ID, LOG_LEVEL


extra = {"app_name": APP_NAME}
logging.basicConfig(level=LOG_LEVEL, format=f"%(asctime)s {APP_NAME}: %(message)s")
logger = logging.getLogger(__name__)
logger = logging.LoggerAdapter(logger, extra)


async def start_server():

    await init_database()
    logger.info("Database initialization completed.")

    producer = BaseProducer(
        client_id=KAFKA_PRODUCER_CLIENT_ID,
        value_serializer=lambda x: dumps(x).encode("utf-8"),
        key_serializer=lambda x: str(x).encode("utf-8")
    )
    await producer.start()
    report_ids_processor = ReportUniqueIds(producer)
    

    file_consumer = JSONConsumer(
        topics=[KAFKA_CONSUMER_TOPIC_NAME],
        group_id=KAFKA_CONSUMER_GROUP_ID,
        client_id=KAFKA_CONSUMER_CLIENT_ID,
        auto_offset_reset=KAFKA_CONSUMER_AUTO_OFFSET_RESET,
        max_poll_records=KAFKA_CONSUMER_MAX_POLL_RECORDS,
        max_poll_interval_ms=KAFKA_CONSUMER_DEFAULT_POLL_TIMEOUT_MS,
        value_deserializer=lambda x: loads(x.decode("utf-8"))
        # heartbeat_interval_ms=KAFKA_CONSUMER_HEARTBEAT_TIME,
        # session_timeout_ms=int(KAFKA_CONSUMER_SESSION_TIME)
    )

    await file_consumer.consume_with_pause(
        execute_func=report_ids_processor.process,
        error_func=report_ids_processor.error_handler,
    )


if __name__ == "__main__":
    asyncio.run(start_server())
