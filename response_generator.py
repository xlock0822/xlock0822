class ResponseGenerator:
    def __init__(self, processed_data):
        self.data = processed_data
        self.templates = self.generate_templates()

    def generate_templates(self):
        print("\n=== Generating Response Templates ===")
        templates = {
            'about': self._generate_about_templates(),
            'services': self._generate_service_templates(),
            'contact': self._generate_contact_templates(),
            'general': self._generate_general_templates()
        }
        print("✅ Templates generated")
        return templates

    def _generate_about_templates(self):
        about = self.data['about']
        return {
            'company_intro': f"Welcome! {about.get('description', '')}",
            'highlights': "Here are our key highlights:\n" + "\n".join(about.get('highlights', [])),
            'full_info': f"{about.get('title', '')}\n\n{about.get('description', '')}"
        }

    def _generate_service_templates(self):
        services = self.data['services']
        templates = {
            'service_list': "Our services include:\n" + "\n".join(
                [f"• {service['name']}" for service in services]
            ),
            'detailed_services': {}
        }
        
        for service in services:
            templates['detailed_services'][service['name']] = {
                'description': service['description'],
                'features': "Features:\n" + "\n".join(
                    [f"• {feature}" for feature in service['features']]
                )
            }
        
        return templates

    def _generate_contact_templates(self):
        contact = self.data['contact']
        return {
            'contact_info': f"You can reach us at:\nEmail: {contact.get('email', 'N/A')}\nPhone: {contact.get('phone', 'N/A')}",
            'location': f"Our address: {contact.get('address', 'N/A')}",
            'full_contact': f"Contact Information:\nEmail: {contact.get('email', 'N/A')}\nPhone: {contact.get('phone', 'N/A')}\nAddress: {contact.get('address', 'N/A')}"
        }

    def _generate_general_templates(self):
        return {
            'greeting': "Hello! How can I assist you today?",
            'farewell': "Thank you for chatting with us. Have a great day!",
            'not_found': "I apologize, but I couldn't find the specific information you're looking for. Would you like me to connect you with our team?",
            'clarification': "Could you please provide more details about what you're looking for?"
        }