from typing import Dict, List
import re
from collections import defaultdict

class SentimentAnalyzer:
    def __init__(self):
        self.sentiment_patterns = {
            "positive": [
                r"\b(great|excellent|awesome|amazing|good|thank|thanks|appreciate)\b",
                r"😊|👍|🙂|❤️"
            ],
            "negative": [
                r"\b(bad|poor|terrible|awful|horrible|upset|angry|frustrated)\b",
                r"😠|👎|😢|😞"
            ],
            "urgent": [
                r"\b(asap|urgent|emergency|immediately|quick)\b",
                r"❗|⚠️"
            ]
        }
        
    def analyze(self, text: str) -> Dict[str, float]:
        """Analyze text sentiment and return scores"""
        text = text.lower()
        scores = defaultdict(float)
        
        for sentiment, patterns in self.sentiment_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                scores[sentiment] += len(matches) * 0.5
        
        # Normalize scores
        max_score = max(scores.values()) if scores else 1
        if max_score > 0:
            for sentiment in scores:
                scores[sentiment] = round(scores[sentiment] / max_score, 2)
        
        return dict(scores)