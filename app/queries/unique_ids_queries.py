

from sqlalchemy import and_, select
from app.context import get_where_clause_with_filter_and_hierarchy, make_join_in_query_for_filters_and_hierarchy, source_table_mapping
from database import get_reports_mongodb
from utils import get_date_range, log_exception


async def build_query_for_unique_ids(query_spec:dict = None, report_data:dict = None):

    company_id = report_data.get("company_id")
    allocation_month = report_data.get("allocation_month")
    allocation_month = allocation_month if allocation_month != "overall" else ""
    report_offset_time = report_data.get("report_offset_time")
    

    from_date, to_date = get_date_range(report_offset_time)
    unique_ids_filters = get_unique_ids_filters(report_data=report_data)

    table_name = query_spec.get("table_name")
    select_fields = query_spec.get("select_fields")
    report_offset_time_key = query_spec.get("report_offset_time_key")
   
    where_condition, join_mapping = await get_where_clause_with_filter_and_hierarchy(
        company_id, where_condition, unique_ids_filters, report_data.get("user_data", {})
    )    

    table_name = source_table_mapping(table_name)

    select_statement = [
        getattr(table_name, select_field) for select_field in select_fields
    ]
    where_condition = [
        getattr(table_name, "company_id") == company_id,
        getattr(table_name, "archive") == False,
        getattr(table_name, "is_delete") == False
    ]
    if allocation_month:
        where_condition.append(getattr(table_name, allocation_month) == allocation_month)
    if report_offset_time_key is not None and from_date and to_date:
        where_condition.append(
            and_(
                getattr(table_name, report_offset_time_key) >= from_date,
                getattr(table_name, report_offset_time_key) <= to_date
            )
        )
    
    query = select(*select_statement).select_from(table_name).where(*where_condition)
    query = await make_join_in_query_for_filters_and_hierarchy(table_name, join_mapping, query)
    query = query.group_by(*select_statement)

    return query

    






async def get_available_filters(report_category:str = None):
    try:
        filters_query = {
            "active": True,
            "report_category": report_category
        }
        reports_mongo_db = get_reports_mongodb()
        available_filters = await reports_mongo_db.filter_mapping.find(filters_query)
        return available_filters
    except Exception as e:
        log_exception(f"Unable to fetch filters for {report_category}")
        raise e



def update_range_keys_filter(request_args, filter, source_table):
    key = filter["filter_key"]
    start_value = request_args.get(f'{key}_start')
    end_value = request_args.get(f'{key}_end')
    if start_value or end_value:
        return [start_value, end_value], filter.get(source_table), True
    return None, filter.get(source_table), True


async def get_unique_ids_filters(report_data:dict = None):

    source_table = "source_table" if report_data.get("company_type", "") == "loan" else "credit_line_source_table"
    available_filters = await get_available_filters(report_data.get("report_category"))
    report_filters = report_data.get("report_filters")

    filters = {}
    for available_filter in available_filters:
        key = available_filter.get("filter_key")
        if available_filter.get("range_from") and available_filter.get("range_to"):
            filters[key] = update_range_keys_filter(report_filters, available_filter, source_table)
        else:
            filters[key] = (report_filters.get(key), available_filter.get(source_table), False)

    return filters

