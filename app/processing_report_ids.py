from cg_kafka.producer.base import BaseProducer
import logging
from app.queries.report_config_queries import get_unique_ids_query_specifications
from app.queries.unique_ids_queries import build_query_for_unique_ids

from database import MongoManager
from settings import APP_NAME, KAFKA_CONSUMER_TOPIC_NAME, LOG_LEVEL, MONGO_DB_REPORT_NAME, REPORT_CATEGORY_BATCH_SIZE_MAPPING, REPORT_MONGO_URI
from utils import async_get_ti_db, create_batches, prepare_batch_message


extra = {"app_name": APP_NAME}

logging.basicConfig(level=LOG_LEVEL, format=f'%(asctime)s - {APP_NAME}:- %(levelname)s - %(funcName)s - %(message)s')
logger = logging.getLogger(__name__)
logger = logging.LoggerAdapter(logger, extra)


class ReportUniqueIds:

    def __init__(self, producer: BaseProducer):
        self.producer = producer

    async def error_handler(self, e, data):
        await self.producer.send_and_wait(
            topic=f"{KAFKA_CONSUMER_TOPIC_NAME}_dlq", value=data.value
        )
        logger.error(f"Produce to DLQ topic Exception::= {str(e)}")

    
    async def process(self, msg):

        data = msg.value
        report_category = data.get("report_category")
        report_type = data.get("report_type")
        module = data.get("module")

        query_spec = get_unique_ids_query_specifications(report_category, report_type, module)
        query = build_query_for_unique_ids(query_spec, data)

        async with async_get_ti_db() as db:
            res = await db.execute(query)
            res = res.fetchall()
        result = [dict(data._mapping) for data in res]

        batch_size = REPORT_CATEGORY_BATCH_SIZE_MAPPING.get(report_category)
        total_batches = (len(result) + batch_size - 1) // batch_size

        for batch, batch_id in create_batches(data, batch_size):
            is_last_batch = (batch_id == total_batches)
            unique_id_message = prepare_batch_message(batch, batch_id, is_last_batch, query_spec)
            msg["unique_ids_data"] = unique_id_message
            await self.producer.send_and_wait(
                topic="report_chunk_ids", value=msg
            )

        












    


    