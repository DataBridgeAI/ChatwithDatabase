from google.cloud import bigquery
from typing import List, Dict, Any

def convert_rows_to_dict(query_result) -> List[Dict[str, Any]]:
    """Convert BigQuery RowIterator to list of dictionaries."""
    return [dict(row.items()) for row in query_result]

def analyze_schema_coverage() -> List[Dict[str, Any]]:
    client = bigquery.Client()
    query = """
    SELECT 
        REGEXP_EXTRACT(generated_sql, r'FROM\s+`[\w-]+\.[\w-]+\.([\w-]+)`') as table_name,
        COUNT(*) as usage_count
    FROM `chatwithdata-451800.Feedback_Dataset.user_feedback`
    GROUP BY table_name
    """
    result = client.query(query).result()
    return convert_rows_to_dict(result)

def analyze_query_distribution() -> List[Dict[str, Any]]:
    client = bigquery.Client()
    query = """
    SELECT 
        REGEXP_EXTRACT(generated_sql, r'WHERE\s+([\w\s=]+)') as filter_condition,
        COUNT(*) as filter_count
    FROM `chatwithdata-451800.Feedback_Dataset.user_feedback`
    GROUP BY filter_condition
    HAVING filter_count > 10
    """
    result = client.query(query).result()
    return convert_rows_to_dict(result)

def analyze_demographic_bias() -> List[Dict[str, Any]]:
    client = bigquery.Client()
    query = """
    SELECT 
        CASE 
            WHEN LOWER(generated_sql) LIKE '%city%' THEN 'City Filter'
            WHEN LOWER(generated_sql) LIKE '%zipcode%' THEN 'Zipcode Filter'
            WHEN LOWER(generated_sql) LIKE '%state%' THEN 'State Filter'
        END as demographic_filter,
        COUNT(*) as usage_count
    FROM `chatwithdata-451800.Feedback_Dataset.user_feedback`
    WHERE LOWER(generated_sql) LIKE '%city%'
        OR LOWER(generated_sql) LIKE '%zipcode%'
        OR LOWER(generated_sql) LIKE '%state%'
    GROUP BY demographic_filter
    """
    result = client.query(query).result()
    return convert_rows_to_dict(result)

def analyze_execution_failures() -> List[Dict[str, Any]]:
    client = bigquery.Client()
    query = """
    SELECT 
        query_type,
        COUNT(*) as failure_count,
        AVG(CASE WHEN feedback = '1' THEN 1 ELSE 0 END) as success_rate
    FROM `chatwithdata-451800.Feedback_Dataset.user_feedback`
    WHERE execution_success = FALSE
    GROUP BY query_type
    """
    result = client.query(query).result()
    return convert_rows_to_dict(result)
