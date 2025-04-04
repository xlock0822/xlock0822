from typing import Dict, List, Tuple
import re
from collections import defaultdict

class IntentAnalyzer:
    def __init__(self):
        self.intent_patterns = {
            "greeting": r"\b(hello|hi|hey|good\s*(morning|afternoon|evening))\b",
            "farewell": r"\b(goodbye|bye|see\s*you|take\s*care)\b",
            "business_hours": r"\b(hours|open|schedule|timing)\b",
            "pricing": r"\b(price|cost|pricing|rate|subscription|plan)\b",
            "support": r"\b(help|support|assist|contact|reach)\b",
            "complaint": r"\b(complaint|problem|issue|unhappy|dissatisfied)\b",
            "product_info": r"\b(product|service|feature|specification|detail)\b",
            "comparison": r"\b(compare|difference|versus|vs|better)\b",
            "availability": r"\b(available|in\s*stock|delivery|shipping)\b",
            "account": r"\b(account|login|signin|signup|password)\b"
        }
        
        self.intent_keywords = defaultdict(list)
        self._initialize_keywords()

    def _initialize_keywords(self):
        """Initialize intent-specific keywords"""
        self.intent_keywords.update({
            "greeting": ["hello", "hi", "hey", "morning", "afternoon", "evening"],
            "farewell": ["goodbye", "bye", "see you", "take care"],
            "urgent": ["urgent", "emergency", "asap", "immediately"],
            "frustrated": ["frustrated", "angry", "upset", "terrible"],
            "positive": ["great", "awesome", "excellent", "thank you"],
            "negative": ["bad", "poor", "terrible", "worst"]
        })

    def analyze(self, text: str) -> Dict[str, float]:
        """
        Analyze text and return confidence scores for each intent
        """
        text = text.lower()
        scores = defaultdict(float)
        
        # Pattern matching
        for intent, pattern in self.intent_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            scores[intent] = len(matches) * 0.5
        
        # Keyword matching
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    scores[intent] += 0.3
        
        # Normalize scores
        max_score = max(scores.values()) if scores else 1
        if max_score > 0:
            for intent in scores:
                scores[intent] = round(scores[intent] / max_score, 2)
        
        return dict(scores)

    def get_primary_intent(self, text: str) -> Tuple[str, float]:
        """Get the primary intent with its confidence score"""
        scores = self.analyze(text)
        if not scores:
            return "general", 0.0
        
        primary_intent = max(scores.items(), key=lambda x: x[1])
        return primary_intent