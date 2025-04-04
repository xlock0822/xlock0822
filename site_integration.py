import asyncio
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='integration_log.txt'
)
logger = logging.getLogger(__name__)

class SiteIntegrator:
    def __init__(self, url):
        self.url = self._format_url(url)
        self.content = {}
        self.sections = {}
        
    def _format_url(self, url):
        if not url.startswith(('http://', 'https://')):
            return f'https://{url}'
        return url
        
    async def integrate(self):
        print("\n=== Starting Site Integration ===")
        print(f"URL: {self.url}")
        
        try:
            # Step 1: Get main page content
            print("\n1. Fetching main page content...")
            response = requests.get(self.url)
            soup = BeautifulSoup(response.text, 'html.parser')
            print("✅ Main page content fetched")

            # Step 2: Extract sections
            print("\n2. Extracting page sections...")
            self.sections = {
                'about': self._extract_section(soup, ['about', 'about-us']),
                'services': self._extract_section(soup, ['services', 'what-we-do']),
                'contact': self._extract_section(soup, ['contact', 'contact-us']),
                'products': self._extract_section(soup, ['products', 'our-products']),
                'pricing': self._extract_section(soup, ['pricing', 'plans', 'packages'])
            }
            print("✅ Sections extracted")

            # Step 3: Process content
            print("\n3. Processing content...")
            self.content = self._process_content(soup)
            print("✅ Content processed")

            # Step 4: Generate response templates
            print("\n4. Generating response templates...")
            templates = self._generate_templates()
            print("✅ Templates generated")

            # Step 5: Save everything
            print("\n5. Saving integration results...")
            self._save_results(templates)
            print("✅ Results saved")

            return True

        except Exception as e:
            print(f"\n❌ Error during integration: {str(e)}")
            logger.error(f"Integration error: {str(e)}")
            return False

    def _extract_section(self, soup, class_names):
        """Extract content from specific sections"""
        for class_name in class_names:
            section = soup.find(['div', 'section'], class_=lambda x: x and class_name in x.lower())
            if not section:
                section = soup.find(['div', 'section'], id=lambda x: x and class_name in x.lower())
            if section:
                return {
                    'text': section.get_text(strip=True),
                    'html': str(section),
                    'links': [a['href'] for a in section.find_all('a', href=True)],
                    'headers': [h.text for h in section.find_all(['h1', 'h2', 'h3', 'h4'])]
                }
        return None

    def _process_content(self, soup):
        """Process and structure the content"""
        return {
            'title': soup.title.string if soup.title else '',
            'meta_description': soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else '',
            'headers': [h.text for h in soup.find_all(['h1', 'h2', 'h3'])],
            'links': [{'text': a.text, 'href': a['href']} for a in soup.find_all('a', href=True)],
            'images': [{'src': img['src'], 'alt': img.get('alt', '')} for img in soup.find_all('img', src=True)],
            'contact_info': self._extract_contact_info(soup),
            'main_content': soup.get_text(separator='\n', strip=True)
        }

    def _extract_contact_info(self, soup):
        """Extract contact information"""
        contact_info = {
            'emails': [],
            'phones': [],
            'social_links': []
        }

        # Find emails
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        contact_info['emails'] = list(set([
            a.text for a in soup.find_all('a', href=lambda x: x and 'mailto:' in x)
        ]))

        # Find phone numbers
        contact_info['phones'] = list(set([
            a.text for a in soup.find_all('a', href=lambda x: x and 'tel:' in x)
        ]))

        # Find social links
        social_platforms = ['facebook', 'twitter', 'linkedin', 'instagram']
        contact_info['social_links'] = [
            link['href'] for link in soup.find_all('a', href=True)
            if any(platform in link['href'].lower() for platform in social_platforms)
        ]

        return contact_info

    def _generate_templates(self):
        """Generate response templates based on content"""
        templates = {
            'greetings': [
                "Hello! Welcome to our site. How can I help you today?",
                "Hi there! I'm here to assist you. What can I do for you?",
                "Welcome! How may I help you today?"
            ],
            'about': self._generate_about_templates(),
            'services': self._generate_service_templates(),
            'contact': self._generate_contact_templates(),
            'general': self._generate_general_templates()
        }
        return templates

    def _generate_about_templates(self):
        about = self.sections.get('about', {})
        if not about:
            return ["I apologize, but I couldn't find specific information about that."]
        
        headers = about.get('headers', [])
        return [
            f"Let me tell you about us: {headers[0]}" if headers else "Let me tell you about us.",
            "Here's what you should know about our company:",
            "Would you like to know more about any specific aspect of our company?"
        ]

    def _generate_service_templates(self):
        services = self.sections.get('services', {})
        if not services:
            return ["I apologize, but I couldn't find specific information about our services."]
        
        headers = services.get('headers', [])
        return [
            f"Here are our services: {', '.join(headers)}" if headers else "Let me tell you about our services.",
            "We offer the following services:",
            "Which service would you like to know more about?"
        ]

    def _generate_contact_templates(self):
        contact = self.content.get('contact_info', {})
        templates = ["Here's how you can reach us:"]
        
        if contact.get('emails'):
            templates.append(f"Email: {contact['emails'][0]}")
        if contact.get('phones'):
            templates.append(f"Phone: {contact['phones'][0]}")
        if contact.get('social_links'):
            templates.append("You can also find us on social media!")
            
        return templates

    def _generate_general_templates(self):
        return [
            "I'm here to help! What would you like to know?",
            "I can help you with information about our products, services, or getting in touch with us.",
            "Is there anything specific you'd like to know about our company?"
        ]

    def _save_results(self, templates):
        """Save integration results"""
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)

        # Save content
        with open('data/site_content.json', 'w') as f:
            json.dump(self.content, f, indent=2)

        # Save sections
        with open('data/site_sections.json', 'w') as f:
            json.dump(self.sections, f, indent=2)

        # Save templates
        with open('data/response_templates.json', 'w') as f:
            json.dump(templates, f, indent=2)

async def main():
    # Your site URL
    url = "deluxe-concha-eb7972.netlify.app"
    
    # Create and run integrator
    integrator = SiteIntegrator(url)
    success = await integrator.integrate()
    
    if success:
        print("\n✅ Integration completed successfully!")
        print("\nGenerated files:")
        print("- data/site_content.json")
        print("- data/site_sections.json")
        print("- data/response_templates.json")
    else:
        print("\n❌ Integration failed. Check integration_log.txt for details.")

if __name__ == "__main__":
    asyncio.run(main())