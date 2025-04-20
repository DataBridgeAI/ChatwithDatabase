from collections import defaultdict
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import requests
import os

logger = logging.getLogger(__name__)

SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')

@dataclass
class InvalidInput:
    query: str
    error_type: str
    timestamp: datetime
    validation_details: Dict

class InputTracker:
    def __init__(self):
        self.invalid_inputs = []
        
    def track_invalid_input(self, query: str, error_type: str, validation_details: Dict):
        """Track an invalid input occurrence and send immediate alert"""
        current_input = InvalidInput(
            query=query,
            error_type=error_type,
            timestamp=datetime.now(),
            validation_details=validation_details
        )
        
        self.invalid_inputs.append(current_input)
        self._generate_alert(current_input)
    
    def _generate_alert(self, invalid_input: InvalidInput):
        """Generate actionable alert for single invalid input"""
        root_cause = self._analyze_root_cause(invalid_input.error_type, [invalid_input.query])
        
        alert = {
            "alert_type": "Invalid Input Detected",
            "timestamp": datetime.now().isoformat(),
            "details": {
                "query": invalid_input.query,
                "error_type": invalid_input.error_type,
                "validation_details": invalid_input.validation_details
            },
            "root_cause_analysis": root_cause,
            "recommended_actions": self._get_recommended_actions(invalid_input.error_type)
        }
        
        self._send_alert(alert)
    
    def _analyze_root_cause(self, error_type: str, sample_queries: List[str]) -> Dict:
        """Analyze root cause based on error type and patterns"""
        if "bias" in error_type.lower():
            return {
                "category": "Bias Detection",
                "likely_cause": "Users attempting to query sensitive demographic data",
                "pattern_detected": "Queries containing bias-related terms or stereotypes"
            }
        elif "relevance" in error_type.lower():
            return {
                "category": "Schema Relevance",
                "likely_cause": "Users unfamiliar with available data schema",
                "pattern_detected": "Queries referencing non-existent tables or fields"
            }
        elif "sql_injection" in error_type.lower():
            return {
                "category": "Security",
                "likely_cause": "Potential security testing or malicious attempts",
                "pattern_detected": "Queries containing SQL injection patterns"
            }
        return {
            "category": "General Validation",
            "likely_cause": "Unclear query patterns or user confusion",
            "pattern_detected": "Mixed validation failures"
        }
    
    def _get_recommended_actions(self, error_type: str) -> List[str]:
        """Get recommended actions based on error type"""
        common_actions = [
            "Review and update input validation rules",
            "Update user documentation with examples of valid queries"
        ]
        
        if "bias" in error_type.lower():
            return common_actions + [
                "Review and enhance bias detection patterns",
                "Update UI to better communicate data access policies"
            ]
        elif "relevance" in error_type.lower():
            return common_actions + [
                "Improve schema documentation visibility",
                "Add schema validation hints in UI"
            ]
        elif "sql_injection" in error_type.lower():
            return common_actions + [
                "Review security policies",
                "Implement additional query sanitization"
            ]
        return common_actions
    
    def _format_slack_message(self, alert: Dict) -> str:
        """Format alert data into a readable Slack message"""
        root_cause = alert["root_cause_analysis"]
        
        message = (
            f"🚨 *{alert['alert_type']}*\n\n"
            f"*Query Details:*\n"
            f"• Error Type: {alert['details']['error_type']}\n"
            f"• Query: `{alert['details']['query']}`\n\n"
            
            f"*Root Cause Analysis:*\n"
            f"• Category: {root_cause['category']}\n"
            f"• Likely Cause: {root_cause['likely_cause']}\n"
            f"• Pattern: {root_cause['pattern_detected']}\n\n"
            
            f"*Recommended Actions:*\n"
            f"{chr(10).join(['• ' + action for action in alert['recommended_actions']])}\n"
        )
        return message

    def _send_alert(self, alert: Dict):
        """Send alert to appropriate channels including Slack"""
        # Log the alert
        logger.warning(f"ALERT: High rate of invalid inputs detected\n{json.dumps(alert, indent=2)}")
        
        try:
            # Format message for Slack
            slack_message = self._format_slack_message(alert)
            
            # Send to Slack
            response = requests.post(
                SLACK_WEBHOOK_URL,
                json={"text": slack_message},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to send Slack alert. Status: {response.status_code}, Response: {response.text}")
            else:
                logger.info("Slack alert sent successfully")
                
        except Exception as e:
            logger.error(f"Error sending Slack alert: {str(e)}")




