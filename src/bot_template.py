import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
import logging
from dataclasses import dataclass
import asyncio
from company_config import CompanyConfig
from intent_analyzer import IntentAnalyzer
from sentiment_analyzer import SentimentAnalyzer
from response_generator import ResponseGenerator

class CompanyBot:
    def __init__(self, company_config: CompanyConfig):
        self.config = company_config
        self.knowledge_base = self._initialize_knowledge_base()
        self.conversation_history = {}
        self.intent_analyzer = IntentAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.response_generator = ResponseGenerator(company_config)
    
    def _initialize_knowledge_base(self) -> Dict:
        """Initialize knowledge base with company-specific information"""
        knowledge = {
            "company_info": {
                "name": self.config.name,
                "description": self.config.description,
                "industry": self.config.industry,
                "website": self.config.website
            },
            "products_services": self.config.products_services,
            "faqs": self.config.faqs,
            "policies": self.config.policies,
            "contact": {
                "email": self.config.support_email,
                "phone": self.config.phone_number,
                "hours": self.config.business_hours,
                "timezone": self.config.timezone
            }
        }
        return knowledge

    def _format_business_hours(self) -> str:
        """Format business hours into readable string"""
        hours_str = []
        for day, times in self.config.business_hours.items():
            hours_str.append(f"{day}: {times['open']} - {times['close']}")
        return ", ".join(hours_str)

    async def generate_response(
        self,
        user_input: str,
        user_id: str,
        context: Optional[Dict] = None
    ) -> Tuple[str, Dict]:
        """Generate a response based on user input and context"""
        # Analyze intent and sentiment
        intent, confidence = self.intent_analyzer.get_primary_intent(user_input)
        sentiment = self.sentiment_analyzer.analyze(user_input)
        
        # Store conversation history
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "user_input": user_input,
            "timestamp": datetime.now().isoformat(),
            "intent": intent,
            "sentiment": sentiment
        })
        
        # Generate response
        response = self.response_generator.generate_response(
            intent=intent,
            sentiment=sentiment,
            context=context
        )
        
        metadata = {
            "intent": intent,
            "intent_confidence": confidence,
            "sentiment": sentiment,
            "timestamp": datetime.now().isoformat()
        }
        
        return response, metadata

    def get_conversation_history(self, user_id: str) -> List[Dict]:
        """Retrieve conversation history for a user"""
        return self.conversation_history.get(user_id, [])

async def create_company_bot(company_data: Dict) -> CompanyBot:
    """Create a new company-specific bot instance"""
    config = CompanyConfig(**company_data)
    return CompanyBot(config)