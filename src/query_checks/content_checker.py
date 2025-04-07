from typing import Optional
import re

# Check if Detoxify is available
try:
    from detoxify import Detoxify
    DETOXIFY_AVAILABLE = True
except ImportError:
    DETOXIFY_AVAILABLE = False

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

def is_sql_command(text: str) -> bool:
    """
    Check if text resembles an SQL command.
    Modular and minimal hardcoding.
    """
    sql_pattern = r'\b[A-Z]{2,}\b'
    return re.search(sql_pattern, text) and (' ' in text or ';' in text)

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

def check_sql_safety(user_query: str) -> Optional[str]:
    """Ensure SQL safety."""
    if is_sql_command(user_query):
        return "Restricted SQL operation detected."
    return None
  
def validate_query(user_query: str) -> Optional[str]:
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
