import asyncio
from datetime import datetime

class LocalTestInterface:
    def __init__(self):
        self.conversation_history = []
        self.commands = {
            '!help': 'Show available commands',
            '!support': 'Get support options',
            '!ticket': 'Create a support ticket',
            '!faq': 'Show FAQ',
            '!status': 'Check system status'
        }

    def show_support_options(self):
        return """
📋 Support Options:
1. Technical Support
2. Billing Support
3. Product Information
4. Account Help

Type the number or category name to select.
"""

    def handle_technical_support(self):
        return """
🔧 Technical Support
-------------------
Common Solutions:
• Check our documentation
• Clear your cache
• Update your browser

Contact: tech.support@example.com
"""

    def handle_billing_support(self):
        return """
💰 Billing Support
----------------
Options:
• View current plan
• Update payment method
• Request refund

Contact: billing@example.com
"""

    def handle_product_info(self):
        return """
📦 Product Information
-------------------
Available Plans:
• Basic: $10/month
• Pro: $25/month
• Enterprise: Custom

Features:
• Cloud Storage
• 24/7 Support
• API Access
"""

    def handle_account_help(self):
        return """
👤 Account Help
-------------
Options:
• Reset password
• Update profile
• Manage settings

Contact: account@example.com
"""

    def create_ticket(self, issue):
        ticket_id = f"TICKET-{len(self.conversation_history) + 1}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""
🎫 Support Ticket Created
----------------------
Ticket ID: {ticket_id}
Issue: {issue}
Status: Open
Created: {timestamp}

We'll respond to your ticket shortly.
"""

    def show_faq(self):
        return """
❓ Frequently Asked Questions
-------------------------
Q: How do I reset my password?
A: Visit the login page and click 'Forgot Password'

Q: Where can I find pricing?
A: Check our pricing page or type '!pricing'

Q: How do I contact support?
A: Email support@example.com or create a ticket

Q: What are your hours?
A: We provide 24/7 support
"""

    def show_help(self):
        help_text = "Available Commands:\n"
        for cmd, desc in self.commands.items():
            help_text += f"{cmd}: {desc}\n"
        return help_text

    def process_input(self, user_input):
        # Log the conversation
        self.conversation_history.append(("user", user_input))
        
        # Process commands
        if user_input.startswith('!'):
            if user_input == '!help':
                response = self.show_help()
            elif user_input == '!support':
                response = self.show_support_options()
            elif user_input.startswith('!ticket'):
                issue = user_input[7:] or "No description provided"
                response = self.create_ticket(issue)
            elif user_input == '!faq':
                response = self.show_faq()
            elif user_input == '!status':
                response = "All systems operational ✅"
            else:
                response = "Unknown command. Type !help for available commands."
        
        # Process support options
        elif user_input.lower() in ['1', 'technical', 'tech']:
            response = self.handle_technical_support()
        elif user_input.lower() in ['2', 'billing']:
            response = self.handle_billing_support()
        elif user_input.lower() in ['3', 'product']:
            response = self.handle_product_info()
        elif user_input.lower() in ['4', 'account']:
            response = self.handle_account_help()
        
        # General inquiries
        else:
            response = f"""
I understand you're asking about: "{user_input}"

How can I help you with this? You can:
1. Create a ticket: !ticket your_issue
2. Check our FAQ: !faq
3. Get support options: !support
"""
        
        # Log the response
        self.conversation_history.append(("bot", response))
        return response

def main():
    interface = LocalTestInterface()
    
    print("🤖 Customer Service Bot Local Interface")
    print("Type '!help' for available commands")
    print("Type 'exit' to quit")
    print("-" * 50)

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