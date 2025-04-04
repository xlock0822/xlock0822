import json
from bs4 import BeautifulSoup
import requests

class ContentProcessor:
    def __init__(self, url):
        self.url = url
        self.processed_data = {
            'about': {},
            'services': {},
            'contact': {},
            'pricing': {},
            'faqs': []
        }

    def process_content(self):
        print("\n=== Processing Website Content ===")
        
        try:
            response = requests.get(self.url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Process each section
            self.process_about_section(soup)
            self.process_services_section(soup)
            self.process_contact_section(soup)
            
            print("\n✅ Content processing complete!")
            return self.processed_data
            
        except Exception as e:
            print(f"\n❌ Error processing content: {str(e)}")
            return None

    def process_about_section(self, soup):
        print("\nProcessing About Section...")
        about_section = soup.find('section', {'id': 'about'}) or soup.find('div', {'class': 'about'})
        if about_section:
            self.processed_data['about'] = {
                'title': about_section.find('h1').text if about_section.find('h1') else '',
                'description': about_section.find('p').text if about_section.find('p') else '',
                'highlights': [li.text for li in about_section.find_all('li')]
            }
            print("✅ About section processed")

    def process_services_section(self, soup):
        print("\nProcessing Services Section...")
        services_section = soup.find('section', {'id': 'services'}) or soup.find('div', {'class': 'services'})
        if services_section:
            services = []
            for service in services_section.find_all('div', {'class': 'service'}):
                services.append({
                    'name': service.find('h3').text if service.find('h3') else '',
                    'description': service.find('p').text if service.find('p') else '',
                    'features': [li.text for li in service.find_all('li')]
                })
            self.processed_data['services'] = services
            print("✅ Services section processed")

    def process_contact_section(self, soup):
        print("\nProcessing Contact Section...")
        contact_section = soup.find('section', {'id': 'contact'}) or soup.find('div', {'class': 'contact'})
        if contact_section:
            self.processed_data['contact'] = {
                'email': contact_section.find('a', href=lambda x: x and '@' in x).text if contact_section.find('a', href=lambda x: x and '@' in x) else '',
                'phone': contact_section.find('a', href=lambda x: x and 'tel:' in x).text if contact_section.find('a', href=lambda x: x and 'tel:' in x) else '',
                'address': contact_section.find('address').text if contact_section.find('address') else ''
            }
            print("✅ Contact section processed")