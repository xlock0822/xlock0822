import openai
from typing import Dict, List, Optional
import json
import os
from datetime import datetime
import logging
from dotenv import load_dotenv

class AICustomerServiceBot:
    def __init__(self, company_data: Dict):
        load_dotenv()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        openai.api_key = self.openai_api_key
        
        self.company_data = company_data
        self.conversation_history = {}
        self.knowledge_base = self._initialize_knowledge_base()
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _initialize_knowledge_base(self) -> Dict:
        """Initialize knowledge base with company information"""
        return {
            "products": self._format_product_knowledge(),
            "policies": self._format_policy_knowledge(),
            "troubleshooting": self._load_troubleshooting_guides(),
            "faqs": self.company_data.get('faqs', []),
            "workflows": self._load_service_workflows()
        }

    def _format_product_knowledge(self) -> Dict:
        """Format product information for AI context"""
        products = {}
        for product in self.company_data.get('products', []):
            products[product['name']] = {
                'description': product.get('description', ''),
                'features': product.get('features', []),
                'pricing': product.get('price', ''),
                'use_cases': product.get('use_cases', []),
                'specifications': product.get('specifications', {}),
                'common_issues': product.get('common_issues', [])
            }
        return products

    def _format_policy_knowledge(self) -> Dict:
        """Format company policies"""
        return {
            'refund': {
                'timeframe': '30 days',
                'conditions': [
                    'Product must be unused',
                    'Original packaging required',
                    'Receipt required'
                ],
                'exceptions': [
                    'Custom orders non-refundable',
                    'Digital products non-refundable'
                ]
            },
            'shipping': {
                'methods': ['Standard', 'Express', 'Next Day'],
                'timeframes': {
                    'Standard': '5-7 business days',
                    'Express': '2-3 business days',
                    'Next Day': 'Next business day'
                }
            },
            'warranty': {
                'duration': '1 year',
                'coverage': [
                    'Manufacturing defects',
                    'Material defects'
                ],
                'exclusions': [
                    'Normal wear and tear',
                    'Misuse or abuse'
                ]
            }
        }

    def _load_troubleshooting_guides(self) -> Dict:
        """Load technical troubleshooting information"""
        return {
            'account_issues': {
                'login_problems': {
                    'symptoms': ['Cannot log in', 'Password not working'],
                    'solutions': [
                        'Clear browser cache',
                        'Reset password',
                        'Check caps lock'
                    ]
                },
                'billing_issues': {
                    'symptoms': ['Payment declined', 'Wrong charge'],
                    'solutions': [
                        'Verify card information',
                        'Contact bank',
                        'Check account balance'
                    ]
                }
            },
            'product_issues': {
                'technical_problems': {
                    'symptoms': ['Not working', 'Error message'],
                    'solutions': [
                        'Restart product',
                        'Update software',
                        'Check connections'
                    ]
                }
            }
        }

    def _load_service_workflows(self) -> Dict:
        """Load customer service workflows"""
        return {
            'refund_request': {
                'steps': [
                    'Verify purchase',
                    'Check refund eligibility',
                    'Process refund',
                    'Send confirmation'
                ],
                'required_info': [
                    'Order number',
                    'Purchase date',
                    'Reason for refund'
                ]
            },
            'technical_support': {
                'steps': [
                    'Identify issue',
                    'Try basic troubleshooting',
                    'Escalate if needed',
                    'Follow up'
                ],
                'required_info': [
                    'Product name',
                    'Issue description',
                    'Steps already tried'
                ]
            }
        }

    async def generate_response(self, user_input: str, user_id: str) -> Dict:
        """Generate AI-enhanced response"""
        try:
            # Get conversation context
            context = self._get_conversation_context(user_id)
            
            # Analyze input
            analysis = await self._analyze_input(user_input)
            
            # Generate response using AI
            response_data = await self._generate_ai_response(
                user_input,
                analysis,
                context
            )
            
            # Update conversation context
            self._update_context(user_id, user_input, response_data)
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return {
                'response': "I apologize, but I encountered an error. Please try again.",
                'error': str(e)
            }

    async def _analyze_input(self, user_input: str) -> Dict:
        """Analyze user input using AI"""
        try:
            # Create analysis prompt
            prompt = f"""
            Analyze the following customer service inquiry:
            "{user_input}"
            
            Provide analysis in JSON format with:
            - Primary intent
            - Secondary intents
            - Sentiment
            - Urgency level
            - Required information
            - Suggested actions
            """
            
            # Get AI analysis
            response = await openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a customer service analysis expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse and return analysis
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            self.logger.error(f"Error analyzing input: {str(e)}")
            return {}

    async def _generate_ai_response(
        self,
        user_input: str,
        analysis: Dict,
        context: Dict
    ) -> Dict:
        """Generate AI response with context"""
        try:
            # Create response prompt
            prompt = self._create_response_prompt(
                user_input,
                analysis,
                context
            )
            
            # Get AI response
            response = await openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse response
            response_data = json.loads(response.choices[0].message.content)
            
            # Add follow-up suggestions
            response_data['suggestions'] = await self._generate_followup_suggestions(
                user_input,
                response_data,
                analysis
            )
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"Error generating AI response: {str(e)}")
            return {
                'response': "I apologize, but I encountered an error. Please try again.",
                'error': str(e)
            }

    def _create_response_prompt(
        self,
        user_input: str,
        analysis: Dict,
        context: Dict
    ) -> str:
        """Create detailed prompt for AI response"""
        return f"""
        User Input: "{user_input}"
        
        Analysis:
        {json.dumps(analysis, indent=2)}
        
        Conversation Context:
        {json.dumps(context, indent=2)}
        
        Company Knowledge Base:
        {json.dumps(self.knowledge_base, indent=2)}
        
        Generate a response that:
        1. Addresses the user's primary intent
        2. Is professional and helpful
        3. Includes relevant information from the knowledge base
        4. Provides next steps or suggestions
        5. Maintains conversation context
        
        Return response in JSON format with:
        - Main response text
        - Related information
        - Required actions
        - Status (resolved/pending/escalated)
        - Confidence level
        """

    def _get_system_prompt(self) -> str:
        """Get system prompt for AI"""
        return f"""
        You are an advanced customer service AI assistant for {self.company_data.get('name', 'our company')}.
        
        Your responsibilities:
        1. Provide accurate, helpful information
        2. Maintain professional, friendly tone
        3. Follow company policies and procedures
        4. Escalate complex issues appropriately
        5. Ensure customer satisfaction
        
        Use the provided knowledge base and context to:
        - Answer questions accurately
        - Solve problems effectively
        - Guide customers through processes
        - Maintain conversation continuity
        """

    async def _generate_followup_suggestions(
        self,
        user_input: str,
        response: Dict,
        analysis: Dict
    ) -> List[str]:
        """Generate relevant follow-up suggestions"""
        try:
            prompt = f"""
            Based on:
            User Input: "{user_input}"
            Response: {json.dumps(response, indent=2)}
            Analysis: {json.dumps(analysis, indent=2)}
            
            Generate 3 relevant follow-up suggestions that would:
            1. Help clarify any unclear points
            2. Guide the customer to related information
            3. Improve their experience
            
            Return as a JSON array of strings.
            """
            
            # Get AI suggestions
            response = await openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a customer service expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            self.logger.error(f"Error generating suggestions: {str(e)}")
            return []

    def _get_conversation_context(self, user_id: str) -> Dict:
        """Get or create conversation context"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = {
                'messages': [],
                'current_topic': None,
                'pending_actions': [],
                'satisfaction_level': None
            }
        return self.conversation_history[user_id]

    def _update_context(
        self,
        user_id: str,
        user_input: str,
        response_data: Dict
    ):
        """Update conversation context"""
        context = self.conversation_history[user_id]
        
        # Add message to history
        context['messages'].append({
            'user_input': user_input,
            'response': response_data,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update topic if changed
        if response_data.get('topic'):
            context['current_topic'] = response_data['topic']
        
        # Update pending actions
        if response_data.get('required_actions'):
            context['pending_actions'].extend(response_data['required_actions'])
        
        # Limit history size
        if len(context['messages']) > 10:
            context['messages'] = context['messages'][-10:]

    async def handle_complex_query(
        self,
        query: str,
        user_id: str,
        additional_context: Optional[Dict] = None
    ) -> Dict:
        """Handle complex customer service scenarios"""
        try:
            # Get base response
            response_data = await self.generate_response(query, user_id)
            
            # Check if escalation is needed
            if self._needs_escalation(response_data):
                return await self._handle_escalation(query, response_data, user_id)
            
            # Check if workflow is needed
            if self._needs_workflow(response_data):
                return await self._handle_workflow(query, response_data, user_id)
            
            # Add enhancement's if needed
            if self._needs_enhancement(response_data):
                response_data = await self._enhance_response(response_data, query, user_id)
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"Error handling complex query: {str(e)}")
            return {
                'response': "I apologize, but I encountered an error. Please try again.",
                'error': str(e)
            }

    def _needs_escalation(self, response_data: Dict) -> bool:
        """Check if query needs escalation"""
        return (
            response_data.get('confidence', 1.0) < 0.7 or
            response_data.get('status') == 'escalated' or
            any(word in str(response_data).lower() for word in ['urgent', 'emergency', 'critical'])
        )

    def _needs_workflow(self, response_data: Dict) -> bool:
        """Check if query needs a workflow"""
        return (
            response_data.get('required_actions') or
            response_data.get('topic') in self.knowledge_base['workflows']
        )

    def _needs_enhancement(self, response_data: Dict) -> bool:
        """Check if response needs enhancement"""
        return (
            not response_data.get('suggestions') or
            response_data.get('confidence', 1.0) < 0.9
        )

    async def _handle_escalation(
        self,
        query: str,
        response_data: Dict,
        user_id: str
    ) -> Dict:
        """Handle escalation to human support"""
        # Add escalation information
        response_data['escalated'] = True
        response_data['escalation_reason'] = self._get_escalation_reason(response_data)
        response_data['next_steps'] = [
            "A customer service representative will contact you shortly",
            "Please have your account information ready",
            "You can continue chatting with me while you wait"
        ]
        
        # Update context
        context = self._get_conversation_context(user_id)
        context['escalated'] = True
        context['escalation_timestamp'] = datetime.now().isoformat()
        
        return response_data

    async def _handle_workflow(
        self,
        query: str,
        response_data: Dict,
        user_id: str
    ) -> Dict:
        """Handle workflow-based responses"""
        workflow_type = response_data.get('topic')
        workflow = self.knowledge_base['workflows'].get(workflow_type)
        
        if workflow:
            response_data['workflow'] = workflow
            response_data['current_step'] = 0
            response_data['required_info'] = workflow['required_info']
            response_data['next_step'] = workflow['steps'][0]
        
        return response_data

    async def _enhance_response(
        self,
        response_data: Dict,
        query: str,
        user_id: str
    ) -> Dict:
        """Enhance response with additional information"""
        # Add related information
        if not response_data.get('related_info'):
            response_data['related_info'] = await self._find_related_info(query)
        
        # Add suggestions if missing
        if not response_data.get('suggestions'):
            response_data['suggestions'] = await self._generate_followup_suggestions(
                query,
                response_data,
                {'intent': response_data.get('topic')}
            )
        
        # Add confidence boosting information
        if response_data.get('confidence', 1.0) < 0.9:
            response_data['supporting_info'] = await self._get_supporting_info(query)
        
        return response_data