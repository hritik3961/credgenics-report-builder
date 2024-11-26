from database import get_reports_mongodb
from settings import MONGO_MAX_TIME_MS

import logging


async def get_unique_ids_query_specifications(report_category:str = None, report_type:str =None, module:str = None):

    try:
        query = {
            "active": True
        }
        if module:
            query["module"] = module
        if report_type:
            query["report_type"] = report_type
        if report_category:
            query["report_category"] = report_category
        projection = {
            "_id": 0,
            "unique_ids_query_specifications": 1,
        }

        reports_mongo_db = get_reports_mongodb()
        data = await reports_mongo_db.report_category_mapping.find_one(query, projection, max_time_ms=MONGO_MAX_TIME_MS)

        if data:
            return data.get("unique_ids_query_specifications", {})
        
    except Exception as e:
        logger.error(f"Exception while updating report entry, report_id: {self.report_id}, data: {data}, "
                        f"error: {e}")
        

