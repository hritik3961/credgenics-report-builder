

from sqlalchemy import and_, func, select
from app.tidb_models import DTMF_IVR, LendingDefaultDetails, LendingLoanDetails, LoanAllocations, Tags, UserHierarchy
from constant import COMPLETE_ACCESS, TABLES_MAPPING
from dateutil.parser import parse

from utils import async_get_ti_db, log_exception


async def get_where_clause_with_filter_and_hierarchy(company_id, where_condition, filters, user_data):
    where_condition, join_mapping = get_where_clause_from_filters(where_condition, filters)

    user_id = user_data.get("user_id", None)
    user_type = user_data.get("user_type", None)

    if user_type not in COMPLETE_ACCESS:

        user_detail = await get_user_detail(company_id, user_id)
        user_path = user_detail.get("path")

        where_condition.extend([
            LoanAllocations.active == True,
            LoanAllocations.is_deleted == False,
            LoanAllocations.user_path.like(
                    func.concat(user_path, '%'))
        ])
        if not join_mapping.get(LoanAllocations):
            join_mapping[LoanAllocations] = True

    return where_condition, join_mapping


def get_where_clause_from_filters(where_condition: list, filters: dict, **kwargs):
    join_mapping = {
        LendingLoanDetails: False,
        LendingDefaultDetails: False,
        Tags: False,
        LoanAllocations: False,
    }
    for key, value in filters.items():
        filter_value = value.get("filter_value")
        source_table = value.get("source_table")
        is_filter_with_range = value.get("is_filter_with_range")
        
        if filter_value is None:
            continue

        source_table = source_table_mapping(source_table)

        if is_filter_with_range:
            if key == "created":
                for i in range(2):
                    if filter_value[i] is not None:
                        filter_value[i] = str(parse(filter_value[i]).date())
                        if i == 0:
                            filter_value[i] += " 00:00:00"
                        else:
                            filter_value[i] += " 23:59:59"
            if filter_value[0] is not None:
                where_condition.append(getattr(source_table, key) >= filter_value[0])
            if filter_value[1] is not None:
                where_condition.append(getattr(source_table, key) <= filter_value[1])
        elif isinstance(filter_value, str):
            where_condition.append(getattr(source_table, key) == filter_value)
        elif isinstance(filter_value, list):
            where_condition.append(getattr(source_table, key).in_(filter_value))
        join_mapping[source_table] = True

    return where_condition, join_mapping


def source_table_mapping(source_table):
    mapping = {
        "lending_loan_details": LendingLoanDetails,
        "lending_default_details": LendingDefaultDetails,
        "tags": Tags,
        "loan_allocations": LoanAllocations,
        "user_hierarchy": UserHierarchy,
        "dtmf_ivr": DTMF_IVR
    }
    return mapping.get(source_table)


async def get_user_detail(company_id, user_id):

    try:
        query = select(
            UserHierarchy.user_id,
            UserHierarchy.company_id,
            UserHierarchy.path
        ).filter(
            UserHierarchy.user_id == user_id,
            UserHierarchy.company_id == company_id,
            UserHierarchy.active == True
        ).limit(1)

        async with async_get_ti_db() as db:
            user = await db.execute(query)
            user = user.fetchall()
            user = user[0]
            return dict(user._mapping)
    except Exception as e:
        log_exception("Unable to get user_path from user_hierarchy", e)
        raise e
    

async def make_join_in_query_for_filters_and_hierarchy(source_table, join_mapping, query, avoid_join=[]):
    source_columns = TABLES_MAPPING[source_table.__name__]
    for key, value in join_mapping.items():
        table = key 
        if table == source_table or table in avoid_join:
            continue
        if value and table.__name__ in TABLES_MAPPING:
            target_columns = TABLES_MAPPING[table.__name__]
            join_conditions = []
            for column in source_columns:
                if column in target_columns:
                    join_conditions.append(getattr(source_table, column) == getattr(table , column))
            if join_conditions:
                query = query.join(table, and_(*join_conditions))

    return query