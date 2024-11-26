
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import traceback

from sqlalchemy import Text, func
from app.tidb_models import LoanAllocations
from constant import ADJUSTED_TIME, COMPLETE_ACCESS, CURRENT
from dateutil.relativedelta import relativedelta

from database import get_ti_db_factory
import logging
from settings import APP_NAME, IS_TIME_ADJUSTMENT_REQUIRED, LOG_LEVEL, MAX_STATEMENT_TIMEOUT

logging.basicConfig(level=LOG_LEVEL, format=f'%(asctime)s - {APP_NAME}:- %(levelname)s - %(funcName)s - %(message)s')
logger = logging.getLogger(__name__)


async def set_query_timeout(connection, database_type="mysql"):
    timeout_ms = MAX_STATEMENT_TIMEOUT * 1000
    db_timeout_keyword = "STATEMENT_TIMEOUT"
    if database_type == "mysql":
        db_timeout_keyword = "MAX_EXECUTION_TIME"
    await connection.execute(Text(f"SET SESSION {db_timeout_keyword} = {timeout_ms}"))
    logger.info(f"{database_type} query timeout set to {MAX_STATEMENT_TIMEOUT} seconds")


@asynccontextmanager
async def async_get_ti_db():
    ti_db_factory = await get_ti_db_factory()
    db = ti_db_factory()
    try:
        await set_query_timeout(db)
        logger.info("Query is Running")
        yield db
    except Exception as e:
        logger.error(f"Something is wrong with Query: {e}")
        await db.rollback()
        raise e
    finally:
        logger.info("Query Executed")
        await db.close()


def log_exception(message, exception):
    logger.error(
        f"{message}._unhandled_exception: %s, traceback: %s",
        exception,
        traceback.extract_tb(exception.__traceback__),
    )


def get_date_range(report_offset_time):
    date_today = datetime.now()
    from_date = date_today
    to_date = date_today
    if isinstance(report_offset_time, int) and report_offset_time >= 0:
        from_date = date_today - timedelta(days=report_offset_time)
        to_date = date_today - timedelta(days=1) if report_offset_time > 0 else date_today
    elif isinstance(report_offset_time, str):
        month_delta = 0 if report_offset_time == CURRENT else -1
        adjusted_month = date_today + relativedelta(months=month_delta)
        first_day_of_month = adjusted_month.replace(day=1)
        last_day_of_month = adjusted_month + relativedelta(day=31)
        from_date = first_day_of_month
        to_date = last_day_of_month
    from_date = from_date.replace(hour=0, minute=0, second=0, microsecond=0)
    to_date = to_date.replace(hour=23, minute=59, second=59)
    if IS_TIME_ADJUSTMENT_REQUIRED:
        from_date = from_date - ADJUSTED_TIME
        to_date = to_date - ADJUSTED_TIME
    return from_date, to_date


def create_batches(data, batch_size):
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size], (i // batch_size) + 1


def prepare_batch_message(batch, batch_id, is_last_batch, query_spec):
    select_fields = query_spec.get("select_fields", [])
    field_data = {field: [item[field] for item in batch] for field in select_fields}

    return {
        "unique_ids_data": {
            "batch_id": batch_id,
            **field_data, 
            "is_last_batch": is_last_batch
        }
    }







