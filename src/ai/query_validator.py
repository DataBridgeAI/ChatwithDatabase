def block_inappropriate_query(user_query):
    """Block inappropriate queries"""
    toxic_keywords = ["fuck", "sex", "shit", "violence"]
    if any(word in user_query.lower() for word in toxic_keywords):
        return "Inappropriate query detected."
    return None

def check_sql_safety(user_query):
    """Ensure SQL safety"""
    sql_blacklist = ["DROP", "DELETE", "ALTER"]
    if any(word in user_query.upper() for word in sql_blacklist):
        return "Restricted SQL operation detected."
    return None
