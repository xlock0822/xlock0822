import requests
from bs4 import BeautifulSoup
import trafilatura
from urllib.parse import urljoin, urlparse
import logging
import json
import re
from typing import Dict, List
from googleapiclient.discovery import build
import asyncio
from datetime import datetime

class CompanyDataIntegrator:
    def __init__(self, website_url: str, google_api_key: str = None):
        self.website_url = website_url
        self.google_api_key = google_api_key
        self.domain = urlparse(website_url).netloc
        self.data = {
            'company_info': {},
            'products': [],
            'faqs': [],
            'support': {},
            'contact': {},
            'policies': {}
        }
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=f'logs/integration_{self.domain}.log'
        )
        self.logger = logging.getLogger(__name__)

    async def integrate(self) -> Dict:
        """Main integration method"""
        try:
            self.logger.info(f"Starting integration for {self.website_url}")
            
            # Parallel execution of data gathering
            tasks = [
                self.gather_website_data(),
                self.search_google_data(),
                self.analyze_social_media(),
                self.check_review_sites()
            ]
            
            await asyncio.gather(*tasks)
            
            # Process and structure the data
            self.process_collected_data()
            
            self.logger.info("Integration completed successfully")
            return self.data
            
        except Exception as e:
            self.logger.error(f"Integration error: {str(e)}")
            raise

    async def gather_website_data(self):
        """Gather data directly from website"""
        try:
            # Get main page
            main_page = await self._get_page_content(self.website_url)
            
            # Extract important URLs
            urls = self._extract_important_urls(main_page)
            
            # Parallel processing of important pages
            tasks = [self._process_page(url) for url in urls]
            await asyncio.gather(*tasks)
            
        except Exception as e:
            self.logger.error(f"Error gathering website data: {str(e)}")

    async def _get_page_content(self, url: str) -> str:
        """Get page content using multiple methods"""
        try:
            # Try trafilatura first
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                content = trafilatura.extract(downloaded)
                if content:
                    return content

            # Fallback to requests
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style']):
                element.decompose()
                
            return soup.get_text()
            
        except Exception as e:
            self.logger.error(f"Error getting content from {url}: {str(e)}")
            return ""

    def _extract_important_urls(self, content: str) -> List[str]:
        """Extract important URLs from content"""
        important_patterns = [
            r'/about',
            r'/product',
            r'/service',
            r'/pricing',
            r'/faq',
            r'/support',
            r'/contact',
            r'/policy',
            r'/terms'
        ]
        
        soup = BeautifulSoup(content, 'html.parser')
        urls = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if any(pattern in href.lower() for pattern in important_patterns):
                full_url = urljoin(self.website_url, href)
                urls.add(full_url)
                
        return list(urls)

    async def _process_page(self, url: str):
        """Process individual pages"""
        content = await self._get_page_content(url)
        
        if 'product' in url.lower() or 'pricing' in url.lower():
            self._extract_product_info(content, url)
        elif 'faq' in url.lower():
            self._extract_faqs(content)
        elif 'support' in url.lower():
            self._extract_support_info(content)
        elif 'contact' in url.lower():
            self._extract_contact_info(content)
        elif 'policy' in url.lower() or 'terms' in url.lower():
            self._extract_policy_info(content)

    async def search_google_data(self):
        """Search Google for additional company information"""
        if not self.google_api_key:
            return

        try:
            service = build('customsearch', 'v1', developerKey=self.google_api_key)
            
            # Search queries
            queries = [
                f"site:{self.domain} products",
                f"site:{self.domain} pricing",
                f"site:{self.domain} support",
                f"{self.domain} reviews",
                f"{self.domain} company information"
            ]
            
            for query in queries:
                result = service.cse().list(q=query, cx='your_search_engine_id').execute()
                self._process_search_results(result.get('items', []))
                
        except Exception as e:
            self.logger.error(f"Error searching Google: {str(e)}")

    async def analyze_social_media(self):
        """Analyze company's social media presence"""
        social_platforms = [
            'linkedin.com',
            'twitter.com',
            'facebook.com',
            'instagram.com'
        ]
        
        for platform in social_platforms:
            try:
                # Search for company profile
                company_name = self.domain.split('.')[0]
                url = f"https://{platform}/{company_name}"
                
                response = requests.get(url)
                if response.status_code == 200:
                    self.data['company_info']['social_media'] = \
                        self.data['company_info'].get('social_media', {})
                    self.data['company_info']['social_media'][platform] = url
                    
            except Exception as e:
                self.logger.error(f"Error analyzing {platform}: {str(e)}")

    async def check_review_sites(self):
        """Check popular review sites"""
        review_sites = [
            'trustpilot.com',
            'g2.com',
            'capterra.com'
        ]
        
        for site in review_sites:
            try:
                url = f"https://{site}/review/{self.domain}"
                response = requests.get(url)
                if response.status_code == 200:
                    self._extract_review_data(response.text, site)
            except Exception as e:
                self.logger.error(f"Error checking {site}: {str(e)}")

    def process_collected_data(self):
        """Process and structure all collected data"""
        # Deduplicate information
        self.data['products'] = list({
            p['name']: p for p in self.data['products']
        }.values())
        
        # Sort FAQs by relevance
        self.data['faqs'].sort(key=lambda x: len(x['answer']), reverse=True)
        
        # Validate and clean data
        self._validate_data()
        
        # Add metadata
        self.data['metadata'] = {
            'last_updated': datetime.now().isoformat(),
            'source_url': self.website_url,
            'confidence_score': self._calculate_confidence()
        }

    def _validate_data(self):
        """Validate collected data"""
        required_fields = {
            'company_info': ['name', 'description'],
            'products': ['name', 'description', 'price'],
            'contact': ['email', 'phone'],
            'support': ['hours', 'channels']
        }
        
        for category, fields in required_fields.items():
            if category in self.data:
                if isinstance(self.data[category], list):
                    for item in self.data[category]:
                        for field in fields:
                            if field not in item:
                                item[field] = "Information not available"
                else:
                    for field in fields:
                        if field not in self.data[category]:
                            self.data[category][field] = "Information not available"

    def _calculate_confidence(self) -> float:
        """Calculate confidence score for collected data"""
        scores = []
        
        # Check company info completeness
        if self.data['company_info']:
            scores.append(len(self.data['company_info']) / 5)  # Expected 5 key pieces
            
        # Check products data
        if self.data['products']:
            scores.append(min(len(self.data['products']) / 3, 1))  # At least 3 products
            
        # Check support info
        if self.data['support']:
            scores.append(len(self.data['support']) / 3)  # Expected 3 key pieces
            
        return sum(scores) / len(scores) if scores else 0.0