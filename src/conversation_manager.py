from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import re

class ConversationContext:
    def __init__(self):
        self.current_topic = None
        self.last_message_time = None
        self.unresolved_questions = []
        self.collected_info = {}
        self.needs_followup = False
        self.interaction_count = 0
        self.satisfaction_level = None
        self.previous_topics = []

class ConversationManager:
    def __init__(self, company_config):
        self.config = company_config
        self.conversations = {}
        self.topic_handlers = self._initialize_topic_handlers()
        self.MAX_IDLE_TIME = timedelta(minutes=30)
        
    def _initialize_topic_handlers(self) -> Dict:
        return {
            "product_inquiry": self._handle_product_inquiry,
            "support_request": self._handle_support_request,
            "complaint": self._handle_complaint,
            "pricing": self._handle_pricing_inquiry,
            "technical_issue": self._handle_technical_issue,
            "billing": self._handle_billing_inquiry,
            "general_info": self._handle_general_inquiry
        }

    async def process_message(self, user_id: str, message: str) -> Tuple[str, Dict]:
        # Get or create conversation context
        context = self._get_or_create_context(user_id)
        
        # Update conversation state
        self._update_conversation_state(context, message)
        
        # Determine message type and topic
        topic, confidence = self._classify_message(message, context)
        
        # Generate appropriate response
        response, new_context = await self._generate_contextual_response(message, context, topic)
        
        # Update context with new information
        self._update_context(context, new_context, topic)
        
        return response, self._create_response_metadata(context, topic, confidence)

    def _get_or_create_context(self, user_id: str) -> ConversationContext:
        # Clear old contexts
        self._cleanup_old_conversations()
        
        if user_id not in self.conversations:
            self.conversations[user_id] = ConversationContext()
        
        context = self.conversations[user_id]
        context.last_message_time = datetime.now()
        return context

    def _cleanup_old_conversations(self):
        current_time = datetime.now()
        expired_users = [
            user_id for user_id, context in self.conversations.items()
            if current_time - context.last_message_time > self.MAX_IDLE_TIME
        ]
        for user_id in expired_users:
            del self.conversations[user_id]

    def _classify_message(self, message: str, context: ConversationContext) -> Tuple[str, float]:
        message = message.lower()
        
        # Define classification patterns
        patterns = {
            "product_inquiry": r"\b(product|service|feature|offering|package)\b",
            "support_request": r"\b(help|support|assist|problem|issue)\b",
            "complaint": r"\b(complaint|unhappy|dissatisfied|wrong|bad|terrible)\b",
            "pricing": r"\b(price|cost|pricing|payment|subscribe|buy)\b",
            "technical_issue": r"\b(error|bug|crash|not working|broken)\b",
            "billing": r"\b(bill|invoice|charge|refund|payment)\b",
            "general_info": r"\b(info|information|about|learn|tell me)\b"
        }
        
        # Check for continuation of previous topic
        if context.current_topic and self._is_topic_continuation(message, context):
            return context.current_topic, 0.8
        
        # Score each pattern
        topic_scores = {}
        for topic, pattern in patterns.items():
            matches = re.findall(pattern, message)
            topic_scores[topic] = len(matches) * 0.3
            
            # Add weight for previous topics
            if topic in context.previous_topics:
                topic_scores[topic] += 0.2
        
        # Get highest scoring topic
        if topic_scores:
            best_topic = max(topic_scores.items(), key=lambda x: x[1])
            return best_topic if best_topic[1] > 0 else ("general_info", 0.5)
        
        return "general_info", 0.5

    async def _generate_contextual_response(
        self,
        message: str,
        context: ConversationContext,
        topic: str
    ) -> Tuple[str, Dict]:
        # Get appropriate handler for the topic
        handler = self.topic_handlers.get(topic, self._handle_general_inquiry)
        
        # Generate response using handler
        response, new_context = await handler(message, context)
        
        # Add follow-up questions if needed
        if context.needs_followup:
            response += self._generate_followup_question(context)
        
        return response, new_context

    async def _handle_product_inquiry(self, message: str, context: ConversationContext) -> Tuple[str, Dict]:
        # Extract specific product mentions
        products = self._extract_product_mentions(message)
        
        if not products and not context.collected_info.get('specific_product'):
            # Ask for specific product interest
            context.needs_followup = True
            context.unresolved_questions.append("specific_product")
            return "I'd be happy to tell you about our products. Which specific product or service are you interested in?", {}
        
        if products:
            context.collected_info['specific_product'] = products[0]
            product_info = self._get_product_info(products[0])
            return f"Let me tell you about {products[0]}. {product_info}", {"product": products[0]}
        
        return self._get_general_product_info(), {}

    async def _handle_support_request(self, message: str, context: ConversationContext) -> Tuple[str, Dict]:
        # Check if we have enough information about the issue
        if not context.collected_info.get('issue_type'):
            context.needs_followup = True
            context.unresolved_questions.append("issue_type")
            return ("I'll help you get the support you need. Could you please describe the issue "
                   "you're experiencing in more detail?"), {}
        
        # Generate appropriate support response
        issue_type = context.collected_info['issue_type']
        support_info = self._get_support_info(issue_type)
        
        return support_info, {"issue_type": issue_type}

    def _generate_followup_question(self, context: ConversationContext) -> str:
        if "specific_product" in context.unresolved_questions:
            return "\n\nWhich of our products would you like to know more about?"
        elif "issue_type" in context.unresolved_questions:
            return "\n\nCould you please provide more details about your issue?"
        return ""

    def _is_topic_continuation(self, message: str, context: ConversationContext) -> bool:
        # Check if message seems to be continuing the current topic
        if not context.current_topic:
            return False
            
        continuation_indicators = [
            "yes", "yeah", "correct", "right", "that's it", "exactly",
            "no", "nope", "different", "something else",
            "what about", "how about", "tell me more"
        ]
        
        return any(indicator in message.lower() for indicator in continuation_indicators)

    def _update_conversation_state(self, context: ConversationContext, message: str):
        context.interaction_count += 1
        context.last_message_time = datetime.now()
        
        # Update satisfaction level based on message content
        satisfaction_indicators = {
            "positive": ["thanks", "great", "helpful", "good", "excellent"],
            "negative": ["unhelpful", "bad", "poor", "terrible", "worst"]
        }
        
        message_lower = message.lower()
        if any(word in message_lower for word in satisfaction_indicators["positive"]):
            context.satisfaction_level = "satisfied"
        elif any(word in message_lower for word in satisfaction_indicators["negative"]):
            context.satisfaction_level = "dissatisfied"

    def _create_response_metadata(self, context: ConversationContext, topic: str, confidence: float) -> Dict:
        return {
            "topic": topic,
            "confidence": confidence,
            "interaction_count": context.interaction_count,
            "satisfaction_level": context.satisfaction_level,
            "needs_followup": context.needs_followup,
            "timestamp": datetime.now().isoformat()
        }

    def _extract_product_mentions(self, message: str) -> List[str]:
        products = []
        for product in self.config.products_services:
            if product['name'].lower() in message.lower():
                products.append(product['name'])
        return products

    def _get_product_info(self, product_name: str) -> str:
        for product in self.config.products_services:
            if product['name'].lower() == product_name.lower():
                return f"{product['description']}. The price is {product['price']}."
        return "I couldn't find specific information about that product."

    def _get_support_info(self, issue_type: str) -> str:
        support_responses = {
            "technical": f"For technical issues, please contact our support team at {self.config.support_email}. "
                        f"Our technical team is available during business hours.",
            "billing": f"For billing-related questions, please email {self.config.support_email} or "
                      f"call us at {self.config.phone_number if self.config.phone_number else 'our support line'}.",
            "general": f"Our support team is here to help! You can reach us at {self.config.support_email} "
                      f"during our business hours: {self._format_business_hours()}"
        }
        return support_responses.get(issue_type, support_responses["general"])

    def _format_business_hours(self) -> str:
        hours = []
        for day, times in self.config.business_hours.items():
            hours.append(f"{day}: {times['open']} - {times['close']}")
        return ", ".join(hours)

    async def _handle_general_inquiry(self, message: str, context: ConversationContext) -> Tuple[str, Dict]:
        return (f"I can help you with information about our products, support, or business hours. "
                f"What would you like to know?"), {}

    async def _handle_complaint(self, message: str, context: ConversationContext) -> Tuple[str, Dict]:
        context.satisfaction_level = "dissatisfied"
        return ("I'm sorry to hear you're having issues. Let me connect you with our support team right away. "
                f"Please contact us at {self.config.support_email} or call {self.config.phone_number if self.config.phone_number else 'our support line'}, "
                "and we'll resolve this as quickly as possible."), {"priority": "high"}

    async def _handle_pricing_inquiry(self, message: str, context: ConversationContext) -> Tuple[str, Dict]:
        # Implementation for pricing inquiries
        pass

    async def _handle_technical_issue(self, message: str, context: ConversationContext) -> Tuple[str, Dict]:
        # Implementation for technical issues
        pass

    async def _handle_billing_inquiry(self, message: str, context: ConversationContext) -> Tuple[str, Dict]:
        # Implementation for billing inquiries
        pass