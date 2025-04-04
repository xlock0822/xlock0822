import asyncio
from datetime import datetime, timedelta
import json
import re
from typing import Dict, List, Optional
import random
import os

class AdvancedResponseHandler:
    def __init__(self):
        self.context = {}
        self.sentiment_patterns = {
            'positive': ['thank', 'good', 'great', 'awesome', 'excellent', 'happy'],
            'negative': ['bad', 'poor', 'terrible', 'unhappy', 'issue', 'problem'],
            'urgent': ['urgent', 'asap', 'emergency', 'immediately']
        }
        
    def analyze_input(self, text: str) -> Dict:
        return {
            'sentiment': self._analyze_sentiment(text),
            'keywords': self._extract_keywords(text),
            'category': self._categorize_query(text),
            'urgency': self._determine_urgency(text)
        }
        
    def _analyze_sentiment(self, text: str) -> str:
        text = text.lower()
        for sentiment, patterns in self.sentiment_patterns.items():
            if any(pattern in text for pattern in patterns):
                return sentiment
        return 'neutral'
    
    def _extract_keywords(self, text: str) -> List[str]:
        common_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but'}
        words = text.lower().split()
        return [word for word in words if word not in common_words]
    
    def _categorize_query(self, text: str) -> str:
        categories = {
            'technical': ['error', 'bug', 'broken', 'not working', 'failed'],
            'billing': ['charge', 'payment', 'invoice', 'refund', 'price'],
            'account': ['login', 'password', 'account', 'profile', 'settings'],
            'product': ['feature', 'product', 'service', 'upgrade', 'plan']
        }
        
        text = text.lower()
        for category, patterns in categories.items():
            if any(pattern in text for pattern in patterns):
                return category
        return 'general'
    
    def _determine_urgency(self, text: str) -> int:
        urgent_patterns = self.sentiment_patterns['urgent']
        text = text.lower()
        return sum(pattern in text for pattern in urgent_patterns)

class LocalTestInterface:
    def __init__(self):
        self.conversation_history = []
        self.active_tickets = {}
        self.user_preferences = {}
        self.response_handler = AdvancedResponseHandler()
        self.setup_commands()
        
    def setup_commands(self):
        self.commands = {
            '!help': self.show_help,
            '!support': self.show_support_options,
            '!ticket': self.create_ticket,
            '!faq': self.show_faq,
            '!status': self.show_status,
            '!preferences': self.manage_preferences,
            '!history': self.show_history,
            '!tickets': self.show_tickets,
            '!search': self.search_knowledge_base,
            '!feedback': self.handle_feedback
        }

    def show_help(self, args: str = "") -> str:
        help_text = """
📚 Available Commands
------------------
!help - Show this help message
!support - Get support options
!ticket [issue] - Create a support ticket
!faq - Show frequently asked questions
!status - Check system status
!preferences - Manage your preferences
!history - View conversation history
!tickets [id] - View support tickets
!search [query] - Search knowledge base
!feedback - Provide feedback

You can also type your question directly and I'll help you!
"""
        return help_text

    def show_status(self, args: str = "") -> str:
        return f"""
📊 System Status
--------------
🟢 API: Operational
🟢 Website: Operational
🟢 Database: Operational
🟢 Support System: Online

Response Times:
• Chat: < 1 minute
• Email: < 1 hour
• Tickets: < 4 hours

Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    def show_faq(self, args: str = "") -> str:
        return """
❓ Frequently Asked Questions
-------------------------
Q: How do I reset my password?
A: Click 'Forgot Password' on the login page and follow the instructions.

Q: How do I upgrade my account?
A: Go to Account Settings > Subscription > Upgrade Plan.

Q: What payment methods do you accept?
A: We accept credit cards, PayPal, and bank transfers.

Q: How do I contact support?
A: You can:
• Create a ticket (!ticket)
• Email: support@example.com
• Call: 1-800-SUPPORT

Q: What are your business hours?
A: We provide 24/7 support with priority handling during 9 AM - 5 PM EST.
"""

    def show_support_options(self, args: str = "") -> str:
        return """
🎯 Support Options
---------------
1. Technical Support
   • System issues
   • Bug reports
   • Feature help

2. Billing Support
   • Payment issues
   • Invoices
   • Refunds

3. Account Support
   • Login help
   • Account settings
   • Security

4. Product Support
   • Features
   • Upgrades
   • Training

Choose a category number or type your question!
"""

    def process_input(self, user_input: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_input, "timestamp": datetime.now()})
        analysis = self.response_handler.analyze_input(user_input)
        
        if user_input.startswith('!'):
            command = user_input.split()[0]
            args = user_input[len(command):].strip()
            
            if command in self.commands:
                response = self.commands[command](args) if args else self.commands[command]()
            else:
                response = "Unknown command. Type !help for available commands."
        else:
            response = self.generate_contextual_response(user_input, analysis)
        
        self.conversation_history.append({"role": "bot", "content": response, "timestamp": datetime.now()})
        return response

    def generate_contextual_response(self, user_input: str, analysis: Dict) -> str:
        if analysis['urgency'] > 0:
            prefix = "🚨 I understand this is urgent. Let me help you right away.\n\n"
        elif analysis['sentiment'] == 'negative':
            prefix = "I'm sorry to hear you're having trouble. Let's resolve this together.\n\n"
        else:
            prefix = "I'd be happy to help you with that.\n\n"

        category_responses = {
            'technical': self.handle_technical_query,
            'billing': self.handle_billing_query,
            'account': self.handle_account_query,
            'product': self.handle_product_query
        }

        if analysis['category'] in category_responses:
            main_response = category_responses[analysis['category']](user_input, analysis)
        else:
            main_response = self.handle_general_query(user_input, analysis)

        suggestions = self.generate_suggestions(analysis)
        return f"{prefix}{main_response}\n\n💡 Suggested next steps:\n{suggestions}"

    def handle_technical_query(self, query: str, analysis: Dict) -> str:
        solutions = [
            "• Check if the service is up: !status",
            "• Clear your browser cache and cookies",
            "• Update to the latest version",
            "• Try in a different browser"
        ]
        
        return f"""🔧 Technical Support

Common Solutions:
{chr(10).join(solutions)}

For immediate assistance:
• Create a ticket: !ticket technical
• Email: tech.support@example.com
• Phone: 1-800-TECH-HELP"""

    def handle_billing_query(self, query: str, analysis: Dict) -> str:
        return f"""💰 Billing Support

Your Options:
• View current plan and charges
• Update payment method
• Request refund or invoice
• Dispute a charge

Current Billing Status:
• Next billing date: {(datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')}
• Payment method: Credit Card (ending in *****)

Need immediate help? Contact our billing team:
• Email: billing@example.com
• Phone: 1-800-BILLING"""

    def handle_account_query(self, query: str, analysis: Dict) -> str:
        return """👤 Account Management

Available Actions:
• Reset password
• Update profile information
• Manage security settings
• View account history

Security Tips:
• Enable two-factor authentication
• Use a strong, unique password
• Regularly review account activity

Need help? Contact account support:
• Email: accounts@example.com"""

    def handle_product_query(self, query: str, analysis: Dict) -> str:
        return """📦 Product Information

Available Plans:
• Basic: $10/month - Essential features
• Pro: $25/month - Advanced features
• Enterprise: Custom pricing - All features

Current Features:
• Cloud storage
• 24/7 support
• API access
• Custom integrations

Want to learn more?
• Schedule a demo: !demo
• View documentation: !docs
• Compare plans: !compare"""

    def handle_general_query(self, query: str, analysis: Dict) -> str:
        return f"""I understand you're asking about: "{query}"

I can help you with:
1. Technical Support
2. Billing Questions
3. Account Management
4. Product Information

Please select a category or type !help for available commands."""

    def generate_suggestions(self, analysis: Dict) -> str:
        common_suggestions = [
            "• Type !help to see all available commands",
            "• Create a support ticket with !ticket",
            "• Check our FAQ with !faq"
        ]
        
        category_suggestions = {
            'technical': [
                "• Review technical documentation",
                "• Check system status",
                "• Contact technical support"
            ],
            'billing': [
                "• Review billing history",
                "• Update payment method",
                "• Download invoices"
            ],
            'account': [
                "• Update security settings",
                "• Review account activity",
                "• Manage preferences"
            ],
            'product': [
                "• Compare plans",
                "• Schedule a demo",
                "• Start free trial"
            ]
        }
        
        suggestions = category_suggestions.get(analysis['category'], common_suggestions)
        return '\n'.join(suggestions)

    def create_ticket(self, issue: str = "") -> str:
        ticket_id = f"TICKET-{len(self.active_tickets) + 1}"
        timestamp = datetime.now()
        
        ticket = {
            "id": ticket_id,
            "issue": issue or "No description provided",
            "status": "open",
            "priority": "normal",
            "created_at": timestamp,
            "updates": []
        }
        
        self.active_tickets[ticket_id] = ticket
        
        return f"""🎫 Support Ticket Created
----------------------
Ticket ID: {ticket_id}
Issue: {ticket['issue']}
Status: {ticket['status'].upper()}
Priority: {ticket['priority'].upper()}
Created: {timestamp.strftime("%Y-%m-%d %H:%M:%S")}

We'll respond to your ticket shortly.
Track your ticket with: !tickets {ticket_id}"""

    def show_tickets(self, ticket_id: str = "") -> str:
        if ticket_id:
            if ticket_id in self.active_tickets:
                ticket = self.active_tickets[ticket_id]
                return f"""🎫 Ticket Details: {ticket_id}
----------------------
Status: {ticket['status'].upper()}
Priority: {ticket['priority'].upper()}
Created: {ticket['created_at'].strftime("%Y-%m-%d %H:%M:%S")}
Issue: {ticket['issue']}

Updates:
{chr(10).join(ticket['updates']) if ticket['updates'] else 'No updates yet'}"""
            else:
                return f"Ticket {ticket_id} not found."
        
        if not self.active_tickets:
            return "No active tickets found."
        
        tickets_list = ""
        for tid, ticket in self.active_tickets.items():
            tickets_list += f"\n{tid}: {ticket['status'].upper()} - {ticket['issue'][:50]}..."
        
        return f"""🎫 Active Tickets
---------------{tickets_list}

View ticket details with: !tickets <ticket_id>"""

    def handle_feedback(self, feedback: str = "") -> str:
        if not feedback:
            return """📝 Feedback Options
-----------------
Rate your experience:
1. Excellent
2. Good
3. Fair
4. Poor

Type: !feedback <rating> <comments>"""
        
        parts = feedback.split(maxsplit=1)
        rating = parts[0]
        comments = parts[1] if len(parts) > 1 else ""
        
        return f"""Thank you for your feedback!
Rating: {rating}
Comments: {comments}

Your feedback helps us improve our service."""

    def manage_preferences(self, args: str = "") -> str:
        if not args:
            return """⚙️ Preferences
-------------
Available settings:
• notification_method (email/sms/both)
• language (en/es/fr)
• timezone (GMT/EST/PST)

Update with: !preferences set <setting> <value>
View current: !preferences view"""
        
        parts = args.split()
        if parts[0] == "set" and len(parts) >= 3:
            setting = parts[1]
            value = ' '.join(parts[2:])
            self.user_preferences[setting] = value
            return f"Updated {setting} to: {value}"
        elif parts[0] == "view":
            if not self.user_preferences:
                return "No preferences set."
            prefs = '\n'.join(f"{k}: {v}" for k, v in self.user_preferences.items())
            return f"Current preferences:\n{prefs}"
        
        return "Invalid preference command. Type !preferences for help."

    def show_history(self, args: str = "") -> str:
        if not self.conversation_history:
            return "No conversation history."
        
        history = ""
        for entry in self.conversation_history[-5:]:  # Show last 5 interactions
            timestamp = entry['timestamp'].strftime("%H:%M:%S")
            role = "You" if entry['role'] == "user" else "Bot"
            history += f"\n[{timestamp}] {role}: {entry['content'][:100]}..."
        
        return f"""📝 Recent Conversation History
---------------------------{history}"""

    def search_knowledge_base(self, query: str = "") -> str:
        if not query:
            return "Please provide a search query: !search <query>"
        
        results = [
            "• How to reset your password (Article #123)",
            "• Common technical issues (Article #456)",
            "• Billing FAQ (Article #789)"
        ]
        
        return f"""🔍 Search Results for: "{query}"
------------------------
{chr(10).join(results)}

For more detailed information, visit our documentation."""

def main():
    interface = LocalTestInterface()
    
    print("""
🤖 Enhanced Customer Service Bot
------------------------------
Type !help for available commands
Type 'exit' to quit
    """)

    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'exit':
                print("\nThank you for using the Customer Service Bot!")
                break
            
            if user_input:
                response = interface.process_input(user_input)
                print("\nBot:", response)
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()