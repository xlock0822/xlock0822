class ContextAnalyzer:
    def __init__(self):
        self.intent_patterns = {
            'product_inquiry': ['product', 'pricing', 'cost', 'plan'],
            'support': ['help', 'issue', 'problem', 'error'],
            'account': ['login', 'account', 'password', 'sign up'],
            'billing': ['bill', 'payment', 'charge', 'invoice']
        }

    def analyze(self, message: str, context: dict = None) -> dict:
        """Analyze user message and context"""
        message = message.lower()
        analysis = {
            'intent': self._detect_intent(message),
            'urgency': self._detect_urgency(message),
            'sentiment': self._detect_sentiment(message)
        }
        return analysis

    def _detect_intent(self, message: str) -> str:
        for intent, patterns in self.intent_patterns.items():
            if any(pattern in message for pattern in patterns):
                return intent
        return 'general'

    def _detect_urgency(self, message: str) -> bool:
        urgent_words = ['urgent', 'asap', 'emergency', 'immediately']
        return any(word in message for word in urgent_words)

    def _detect_sentiment(self, message: str) -> str:
        positive = ['thanks', 'good', 'great', 'awesome', 'helpful']
        negative = ['bad', 'poor', 'terrible', 'unhappy', 'wrong']
        
        if any(word in message for word in negative):
            return 'negative'
        if any(word in message for word in positive):
            return 'positive'
        return 'neutral'