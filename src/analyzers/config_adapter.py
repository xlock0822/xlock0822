class ConfigAdapter:
    def __init__(self, website_data: dict):
        self.website_data = website_data

    def generate_bot_config(self) -> dict:
        """Convert website data into bot configuration"""
        return {
            "name": self.website_data.get('company_info', {}).get('name', 'Company Name'),
            "description": self.website_data.get('company_info', {}).get('description', ''),
            "products_services": self._format_products(),
            "faqs": self.website_data.get('faqs', []),
            "support_info": self._format_support_info(),
            "contact_info": self._format_contact_info(),
            "pricing": self._format_pricing()
        }

    def _format_products(self) -> list:
        """Format products/services data"""
        return [{
            'name': product.get('name', ''),
            'description': product.get('description', ''),
            'features': product.get('features', []),
            'price': product.get('price', 'Contact for pricing')
        } for product in self.website_data.get('products_services', [])]

    def _format_support_info(self) -> dict:
        """Format support information"""
        support_info = self.website_data.get('support_info', {})
        return {
            'hours': support_info.get('hours', '24/7'),
            'channels': support_info.get('channels', ['email', 'phone']),
            'contact': support_info.get('contact', {})
        }

    def _format_contact_info(self) -> dict:
        """Format contact information"""
        contact_info = self.website_data.get('contact_info', {})
        return {
            'email': contact_info.get('email', []),
            'phone': contact_info.get('phone', []),
            'address': contact_info.get('address', ''),
            'social_media': contact_info.get('social_media', {})
        }

    def _format_pricing(self) -> list:
        """Format pricing information"""
        return [{
            'name': plan.get('name', ''),
            'price': plan.get('price', ''),
            'features': plan.get('features', [])
        } for plan in self.website_data.get('pricing', [])]