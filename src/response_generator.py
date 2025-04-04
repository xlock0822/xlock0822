from typing import Dict, Optional
import random
from datetime import datetime

class ResponseGenerator:
    def __init__(self, company_config):
        self.config = company_config
        self._initialize_responses()
    
    def _initialize_responses(self):
        self.responses = {
            "products": [
                f"We offer several products at {self.config.name}:\n" + 
                "\n".join([f"• {p['name']}: {p['description']} ({p['price']})" 
                          for p in self.config.products_services]),
                "Let me tell you about our products. " +
                "\n".join([f"• {p['name']} - {p['description']}" 
                          for p in self.config.products_services])
            ],
            "support": [
                f"I'll help you get in touch with our support team. You can reach us at {self.config.support_email} "
                f"or call us at {self.config.phone_number if self.config.phone_number else 'our support email'}.",
                f"Our support team is here to help! Contact us at {self.config.support_email} "
                f"during business hours ({self._format_hours()})."
            ],
            "general": [
                "I understand you're looking for information. Could you please specify what you'd like to know about?",
                "I'd be happy to help. What specific information are you looking for?",
                f"I can help you with information about our products, support, or business hours. What would you like to know?"
            ]
        }

    def _format_hours(self):
        hours = []
        for day, times in self.config.business_hours.items():
            hours.append(f"{day}: {times['open']} - {times['close']}")
        return ", ".join(hours)

    def generate_response(self, query: str, context: Optional[Dict] = None) -> str:
        # Identify the type of query and generate appropriate response
        query = query.lower()
        
        if any(word in query for word in ["product", "service", "offer", "price"]):
            return random.choice(self.responses["products"])
            
        if any(word in query for word in ["support", "help", "contact", "reach"]):
            return random.choice(self.responses["support"])
            
        if any(word in query for word in ["hello", "hi", "hey"]):
            return f"Hello! Welcome to {self.config.name}. How can I assist you today?"
            
        if any(word in query for word in ["bye", "goodbye", "thank"]):
            return f"Thank you for contacting {self.config.name}. Have a great day!"
            
        # Default response
        return random.choice(self.responses["general"])