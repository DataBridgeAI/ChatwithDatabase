from typing import Optional
import re

# Check if Detoxify is available
try:
    from detoxify import Detoxify
    DETOXIFY_AVAILABLE = True
except ImportError:
    DETOXIFY_AVAILABLE = False
    print("Warning: Detoxify package not available. Using fallback content checking.")

def check_sql_safety(user_query):
    """Commands that try to modify the structure or data in the shema"""
    sql_blacklist = ["DROP", "DELETE", "ALTER", "INSERT", "TRUNCATE", "UPDATE"]  # Add more keywords if necessary

    # Case-insensitive check for blacklisted SQL commands
    if any(word in user_query.upper() for word in sql_blacklist):
        return "🚫 Restricted SQL operation detected."
    return None

def is_toxic(query: str) -> bool:
    """Check if the query contains toxic language."""
    if DETOXIFY_AVAILABLE:
        toxicity_score = Detoxify('original').predict(query)["toxicity"]
        return toxicity_score > 0.7  # Threshold (can be adjusted)
    else:
        # Fallback: Simple keyword-based check
        toxic_words = ["stupid", "idiot", "hate", "kill", "damn"]
        return any(word in query.lower() for word in toxic_words)

def validate_query(user_query: str) -> str:
    """Validate query for toxicity and SQL safety."""
    # check for SQL safety issues
    sql_error = check_sql_safety(user_query)
    if sql_error:
        return sql_error

    # check if the query is toxic
    if is_toxic(user_query):
        return "🚫 Query contains harmful language. Please modify your input."

    return None  # No issues detected, query is safe



# Centralized sensitivity detector
def analyze_with_detoxify(text: str) -> dict:
    """Use Detoxify to analyze text if available, return empty dict otherwise."""
    if DETOXIFY_AVAILABLE:
        return Detoxify('original').predict(text)
    return {}

def is_sensitive(text: str, detoxify_results: dict = None) -> bool:
    """
    Check if text is sensitive (religion, gender, race, etc.).
    Modular and reusable.
    """
    text = text.lower()
    detoxify_results = detoxify_results or analyze_with_detoxify(text)

    if detoxify_results:
        # Detoxify-based detection for religion, gender, etc.
        return (detoxify_results.get('toxicity', 0) > 0.7 or
                detoxify_results.get('identity_attack', 0) > 0.5 or
                detoxify_results.get('insult', 0) > 0.5)
    else:
        # Fallback: Structural detection for probing questions
        probe_pattern = r'\b(what|which|who|why|how|is|are|best|worst|better|worse)\b'
        relational_clue = r'\b(of|in|for|about|than)\b'
        return (re.search(probe_pattern, text) and re.search(relational_clue, text))

def is_harmful(text: str, detoxify_results: dict = None) -> bool:
    """
    Check if text suggests harmful intent (terrorism, violence).
    Modular and reusable.
    """
    text = text.lower()
    detoxify_results = detoxify_results or analyze_with_detoxify(text)

    if detoxify_results:
        # Detoxify-based detection for harmful intent
        return (detoxify_results.get('threat', 0) > 0.5 or
                detoxify_results.get('obscene', 0) > 0.5)
    else:
        # Fallback: Action-oriented harmful intent
        action_pattern = r'\b(how|do|make|start|plan)\b'
        harm_pattern = r'\b(war|kill|attack)\b'
        return (re.search(action_pattern, text) and re.search(harm_pattern, text))

# def is_sql_command(text: str) -> bool:
#     """
#     Check if text resembles an SQL command.
#     Modular and minimal hardcoding.
#     """
#     sql_pattern = r'\b[A-Z]{2,}\b'
#     return re.search(sql_pattern, text) and (' ' in text or ';' in text)

def detect_sensitive_content(text: str) -> Optional[str]:
    """Detect and respond to sensitive content (religion, gender, etc.)."""
    results = analyze_with_detoxify(text) if DETOXIFY_AVAILABLE else {}
    if is_sensitive(text, results):
        return "🤝 This query might touch on a sensitive topic (e.g., religion, gender). Let’s focus on neutral questions."
    return None

def block_inappropriate_query(user_query: str) -> Optional[str]:
    """Block queries with harmful intent (e.g., terrorism)."""
    results = analyze_with_detoxify(user_query) if DETOXIFY_AVAILABLE else {}
    if is_harmful(user_query, results):
        return "This query suggests harmful intent (e.g., terrorism, violence). I can’t assist with that."
    return None

# def check_sql_safety(user_query: str) -> Optional[str]:
#     """Ensure SQL safety."""
#     if is_sql_command(user_query):
#         return "Restricted SQL operation detected."
#     return None

def sensitivity_filter(user_query: str) -> Optional[str]:
    """
    Validate query by checking sensitivity, intent, and SQL safety.
    Modular structure.
    """
    checks = [
        detect_sensitive_content,
        block_inappropriate_query,
        check_sql_safety
    ]

    for check in checks:
        result = check(user_query)
        if result:
            return result
    return None  # Query is safe
