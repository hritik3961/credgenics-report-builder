import logging

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from settings import MONGO_DB_REPORT_NAME, REPORT_MONGO_URI, TIDB_CONF, MAX_POOL_CONNECT_TIMEOUT
from motor.motor_asyncio import AsyncIOMotorClient

ti_db_factory = None
reports_mongo_manager = None

logger = logging.getLogger(__name__)


async def create_ti_db_factory():
    ti_db_engine = create_async_engine(
        URL.create(
            drivername="mysql+aiomysql",
            username=TIDB_CONF.get("USER"),
            password=TIDB_CONF.get("PASSWORD"),
            host=TIDB_CONF.get("HOST"),
            port=TIDB_CONF.get("PORT"),
            database=TIDB_CONF.get("DB_NAME"),
        ),
        isolation_level="READ COMMITTED",
        pool_size=40,
        max_overflow=10,
        pool_pre_ping=True,
        pool_timeout=MAX_POOL_CONNECT_TIMEOUT
    )
    async_sessionmaker = sessionmaker(ti_db_engine, class_=AsyncSession)
    return async_sessionmaker


class MongoManager:
    _database = None

    def __init__(self, mongo_db, mongo_uri):
        if self._database is None:
            self._client = AsyncIOMotorClient(mongo_uri)
            self._database = self._client[mongo_db]

    def get_database(self):
        if not self._database:
            MongoManager()
        return self._database

    def __del__(self):
        self._client.close()


async def init_database():
    logger.info("Getting database instance..")
    global ti_db_factory
    global reports_mongo_manager

    if not ti_db_factory:
        ti_db_factory = await create_ti_db_factory()

    if not reports_mongo_manager:
        reports_mongo_manager = MongoManager(mongo_db=MONGO_DB_REPORT_NAME, mongo_uri=REPORT_MONGO_URI)


async def get_ti_db_factory():
    global ti_db_factory
    if not ti_db_factory:
        ti_db_factory = await create_ti_db_factory()
    return ti_db_factory


def get_reports_mongodb():
    if reports_mongo_manager is None:
        raise RuntimeError("Reports MongoManager is not initialized")
    return reports_mongo_manager.get_database()

