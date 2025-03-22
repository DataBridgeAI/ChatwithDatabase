import re

class BiasDetector:
    def __init__(self):
        # Comprehensive bias patterns
        self.bias_patterns = {
            'demographic': [
                r'\b(all|every|none|no)\s+(men|women|people|americans|asians|africans|europeans)\b',
                r'\b(typical|always|never)\s+(man|woman|asian|african|european|american)\b',
                r'\b(these|those)\s+(people|folks)\b'
            ],
            'age': [
                r'\b(all|every|none|no)\s+(young|old|elderly|millennials|boomers)\b',
                r'\b(typical|always|never)\s+(young|old)\s+(person|people)\b'
            ],
            'gender': [
                r'\b(all|every)\s+(males?|females?|men|women)\s+(are|should|must|will)\b',
                r'\b(like\s+a|typical)\s+(man|woman|girl|boy)\b'
            ],
            'stereotyping': [
                r'\b(obviously|clearly|naturally|of\s+course)\b',
                r'\b(always|never|every\s+time)\b',
                r'\b(those|these)\s+kind\s+of\b'
            ],
            'absolute_language': [
                r'\b(everyone|nobody|anybody|all\s+people)\s+(knows|thinks|believes|agrees)\b',
                r'\b(without\s+exception|in\s+every\s+case|invariably)\b'
            ]
        }

    def check_bias(self, text: str) -> tuple[bool, str]:
        """
        Check for bias in the input text using pattern matching.
        Returns (is_biased: bool, explanation: str)
        """
        text = text.lower()
        
        for bias_type, patterns in self.bias_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    explanation = self._get_bias_explanation(bias_type)
                    return True, explanation
        
        return False, ""

    def _get_bias_explanation(self, bias_type: str) -> str:
        """Generate a helpful explanation based on the type of bias detected."""
        explanations = {
            'demographic': "The question contains demographic generalizations",
            'age': "The question makes broad assumptions about age groups",
            'gender': "The question contains gender-based assumptions",
            'stereotyping': "The question includes stereotyping language",
            'absolute_language': "The question uses absolute or overly generalized statements"
        }
        return explanations.get(bias_type, "The question contains potential bias")
