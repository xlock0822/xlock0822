import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse
import trafilatura
import re
from typing import Dict, List, Set

class WebsiteAnalyzer:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.data = {
            'company_info': {},
            'products_services': [],
            'faqs': [],
            'support_info': {},
            'pricing': [],
            'contact_info': {}
        }
        self.visited_urls: Set[str] = set()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    async def analyze_website(self) -> Dict:
        """Main method to analyze website and extract information"""
        try:
            # Analyze main page
            await self._analyze_main_page()
            
            # Find and analyze important pages
            await self._find_important_pages()
            
            # Extract structured data
            await self._extract_structured_data()
            
            return self.data
        except Exception as e:
            print(f"Error analyzing website: {str(e)}")
            return {}

    async def _analyze_main_page(self):
        """Analyze the main page for basic company information"""
        try:
            response = requests.get(self.base_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract company name
            self.data['company_info']['name'] = self._extract_company_name(soup)
            
            # Extract description/about
            self.data['company_info']['description'] = self._extract_description(soup)
            
            # Extract contact information
            self.data['contact_info'] = self._extract_contact_info(soup)
            
        except Exception as e:
            print(f"Error analyzing main page: {str(e)}")

    async def _find_important_pages(self):
        """Find and analyze important pages like pricing, support, etc."""
        important_paths = [
            '/pricing', '/price', '/plans',
            '/support', '/help', '/contact',
            '/about', '/about-us',
            '/faq', '/faqs',
            '/products', '/services'
        ]
        
        for path in important_paths:
            url = urljoin(self.base_url, path)
            if url not in self.visited_urls:
                await self._analyze_page(url)

    async def _analyze_page(self, url: str):
        """Analyze a specific page"""
        try:
            self.visited_urls.add(url)
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Determine page type and extract accordingly
            if any(x in url.lower() for x in ['/price', '/plan']):
                self._extract_pricing(soup)
            elif any(x in url.lower() for x in ['/faq', '/help']):
                self._extract_faqs(soup)
            elif any(x in url.lower() for x in ['/product', '/service']):
                self._extract_products_services(soup)
            elif '/support' in url.lower():
                self._extract_support_info(soup)
                
        except Exception as e:
            print(f"Error analyzing page {url}: {str(e)}")

    def _extract_company_name(self, soup) -> str:
        """Extract company name from various possible locations"""
        possible_elements = [
            soup.find('meta', property='og:site_name'),
            soup.find('meta', property='og:title'),
            soup.find('title'),
            soup.find(class_=re.compile(r'.*logo.*')),
            soup.find(class_=re.compile(r'.*brand.*'))
        ]
        
        for element in possible_elements:
            if element:
                if element.get('content'):
                    return element['content']
                elif element.string:
                    return element.string.strip()
        
        return "Company Name Not Found"

    def _extract_description(self, soup) -> str:
        """Extract company description"""
        possible_elements = [
            soup.find('meta', property='og:description'),
            soup.find('meta', name='description'),
            soup.find(class_=re.compile(r'.*about.*')),
            soup.find(class_=re.compile(r'.*description.*'))
        ]
        
        for element in possible_elements:
            if element:
                if element.get('content'):
                    return element['content']
                elif element.string:
                    return element.string.strip()
        
        return "Description Not Found"

    def _extract_contact_info(self, soup) -> Dict:
        """Extract contact information"""
        contact_info = {
            'email': self._find_emails(soup),
            'phone': self._find_phone_numbers(soup),
            'address': self._find_address(soup),
            'social_media': self._find_social_media(soup)
        }
        return contact_info

    def _extract_pricing(self, soup):
        """Extract pricing information"""
        pricing_elements = soup.find_all(class_=re.compile(r'.*price.*|.*plan.*'))
        
        for element in pricing_elements:
            price_info = {
                'name': self._find_plan_name(element),
                'price': self._find_price(element),
                'features': self._find_features(element)
            }
            if price_info['name'] and price_info['price']:
                self.data['pricing'].append(price_info)

    def _extract_faqs(self, soup):
        """Extract FAQ information"""
        faq_elements = soup.find_all(class_=re.compile(r'.*faq.*|.*question.*'))
        
        for element in faq_elements:
            question = element.find(class_=re.compile(r'.*question.*|.*header.*'))
            answer = element.find(class_=re.compile(r'.*answer.*|.*content.*'))
            
            if question and answer:
                self.data['faqs'].append({
                    'question': question.text.strip(),
                    'answer': answer.text.strip()
                })

    def _extract_products_services(self, soup):
        """Extract products/services information"""
        product_elements = soup.find_all(class_=re.compile(r'.*product.*|.*service.*'))
        
        for element in product_elements:
            product_info = {
                'name': self._find_product_name(element),
                'description': self._find_product_description(element),
                'features': self._find_features(element)
            }
            if product_info['name']:
                self.data['products_services'].append(product_info)

    def _extract_support_info(self, soup):
        """Extract support information"""
        support_info = {
            'hours': self._find_support_hours(soup),
            'channels': self._find_support_channels(soup),
            'contact': self._find_support_contact(soup)
        }
        self.data['support_info'].update(support_info)

    # Helper methods for finding specific information
    def _find_emails(self, soup) -> List[str]:
        """Find email addresses"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return list(set(re.findall(email_pattern, str(soup))))

    def _find_phone_numbers(self, soup) -> List[str]:
        """Find phone numbers"""
        phone_pattern = r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        return list(set(re.findall(phone_pattern, str(soup))))

    def _find_address(self, soup) -> str:
        """Find physical address"""
        address_elements = soup.find_all(class_=re.compile(r'.*address.*'))
        for element in address_elements:
            if element.text.strip():
                return element.text.strip()
        return ""

    def _find_social_media(self, soup) -> Dict[str, str]:
        """Find social media links"""
        social_media = {}
        social_platforms = ['facebook', 'twitter', 'linkedin', 'instagram']
        
        for platform in social_platforms:
            links = soup.find_all('a', href=re.compile(f'.*{platform}.*'))
            if links:
                social_media[platform] = links[0]['href']
        
        return social_media

    def _find_plan_name(self, element) -> str:
        """Find plan name"""
        name_element = element.find(class_=re.compile(r'.*name.*|.*title.*'))
        return name_element.text.strip() if name_element else ""

    def _find_price(self, element) -> str:
        """Find price"""
        price_element = element.find(class_=re.compile(r'.*price.*|.*amount.*'))
        return price_element.text.strip() if price_element else ""

    def _find_features(self, element) -> List[str]:
        """Find features"""
        features = []
        feature_elements = element.find_all(class_=re.compile(r'.*feature.*'))
        for feature in feature_elements:
            if feature.text.strip():
                features.append(feature.text.strip())
        return features

    def _find_product_name(self, element) -> str:
        """Find product name"""
        name_element = element.find(class_=re.compile(r'.*name.*|.*title.*'))
        return name_element.text.strip() if name_element else ""

    def _find_product_description(self, element) -> str:
        """Find product description"""
        desc_element = element.find(class_=re.compile(r'.*description.*|.*content.*'))
        return desc_element.text.strip() if desc_element else ""

    def _find_support_hours(self, soup) -> str:
        """Find support hours"""
        hours_element = soup.find(class_=re.compile(r'.*hours.*|.*schedule.*'))
        return hours_element.text.strip() if hours_element else ""

    def _find_support_channels(self, soup) -> List[str]:
        """Find support channels"""
        channels = []
        channel_elements = soup.find_all(class_=re.compile(r'.*channel.*|.*contact.*'))
        for channel in channel_elements:
            if channel.text.strip():
                channels.append(channel.text.strip())
        return channels

    def _find_support_contact(self, soup) -> Dict[str, str]:
        """Find support contact information"""
        return {
            'email': self._find_emails(soup),
            'phone': self._find_phone_numbers(soup)
        }

    async def _extract_structured_data(self):
        """Extract structured data (Schema.org, etc.)"""
        try:
            response = requests.get(self.base_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find JSON-LD data
            script_tags = soup.find_all('script', type='application/ld+json')
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    self._process_structured_data(data)
                except:
                    continue
                    
        except Exception as e:
            print(f"Error extracting structured data: {str(e)}")

    def _process_structured_data(self, data: Dict):
        """Process structured data"""
        if isinstance(data, dict):
            if data.get('@type') == 'Organization':
                self.data['company_info'].update({
                    'name': data.get('name', self.data['company_info'].get('name')),
                    'description': data.get('description', self.data['company_info'].get('description')),
                    'url': data.get('url'),
                    'logo': data.get('logo')
                })
            elif data.get('@type') == 'Product':
                self.data['products_services'].append({
                    'name': data.get('name'),
                    'description': data.get('description'),
                    'price': data.get('offers', {}).get('price')
                })