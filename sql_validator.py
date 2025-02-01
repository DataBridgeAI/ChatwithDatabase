import sqlparse

def validate_and_rank_sql(sql_candidates):
    valid_queries = []
    
    for sql in sql_candidates:
        parsed = sqlparse.parse(sql)
        if parsed:
            valid_queries.append(sql)
    
    return valid_queries[0] if valid_queries else None
