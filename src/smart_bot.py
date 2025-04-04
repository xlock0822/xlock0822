import asyncio
from typing import Dict
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller
from bs4 import BeautifulSoup
import json
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebsiteAnalyzer:
    def __init__(self, url: str):
        self.url = url
        self.driver = None
        self.logger = logging.getLogger(__name__)

    def setup_driver(self):
        try:
            chromedriver_autoinstaller.install()
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            self.logger.error(f"Failed to setup Chrome driver: {e}")
            raise

    def analyze(self) -> Dict:
        try:
            self.driver = self.setup_driver()
            self.logger.info(f"Analyzing website: {self.url}")
            
            self.driver.get(self.url)
            time.sleep(5)  # Wait for dynamic content
            
            # Extract data
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            data = {
                'company_info': self._extract_company_info(soup),
                'products': self._extract_products(soup),
                'contact': self._extract_contact_info(soup),
                'faqs': self._extract_faqs(soup),
                'support': self._extract_support_info(soup)
            }
            
            return data
        except Exception as e:
            self.logger.error(f"Error analyzing website: {e}")
            return {}
        finally:
            if self.driver:
                self.driver.quit()

    def _extract_company_info(self, soup) -> Dict:
        info = {}
        try:
            info['name'] = self.driver.title
            
            # Try to get meta description
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc:
                info['description'] = meta_desc.get('content', '')
                
            # Try to get main content description
            main_content = soup.find(['main', 'article'])
            if main_content:
                info['description'] = main_content.get_text()[:500]  # First 500 chars
                
        except Exception as e:
            self.logger.error(f"Error extracting company info: {e}")
        return info

    def _extract_products(self, soup) -> list:
        products = []
        try:
            # Look for product elements
            product_elements = soup.find_all(['div', 'article'], 
                class_=lambda x: x and ('product' in x.lower() or 'item' in x.lower()))
            
            for element in product_elements[:10]:  # Limit to 10 products
                product = {}
                
                # Try to get product name
                name_elem = element.find(['h1', 'h2', 'h3', 'h4'], 
                    class_=lambda x: x and ('name' in x.lower() or 'title' in x.lower()))
                if name_elem:
                    product['name'] = name_elem.get_text().strip()
                
                # Try to get product price
                price_elem = element.find(class_=lambda x: x and 'price' in x.lower())
                if price_elem:
                    product['price'] = price_elem.get_text().strip()
                
                if product:
                    products.append(product)
                    
        except Exception as e:
            self.logger.error(f"Error extracting products: {e}")
        return products

    def _extract_contact_info(self, soup) -> Dict:
        contact = {}
        try:
            # Find phone numbers
            phone_elements = soup.find_all(text=lambda x: x and any(p in x.lower() for p in ['phone:', 'tel:', 'call us']))
            if phone_elements:
                contact['phone'] = phone_elements[0].strip()
            
            # Find email addresses
            email_elements = soup.find_all('a', href=lambda x: x and 'mailto:' in x.lower())
            if email_elements:
                contact['email'] = email_elements[0]['href'].replace('mailto:', '')
            
            # Find address
            address_elem = soup.find(['address', 'div'], class_=lambda x: x and 'address' in x.lower())
            if address_elem:
                contact['address'] = address_elem.get_text().strip()
                
        except Exception as e:
            self.logger.error(f"Error extracting contact info: {e}")
        return contact

    def _extract_faqs(self, soup) -> list:
        faqs = []
        try:
            # Look for FAQ sections
            faq_elements = soup.find_all(['div', 'section'], 
                class_=lambda x: x and ('faq' in x.lower() or 'accordion' in x.lower()))
            
            for element in faq_elements:
                question = element.find(class_=lambda x: x and 'question' in x.lower())
                answer = element.find(class_=lambda x: x and 'answer' in x.lower())
                
                if question and answer:
                    faqs.append({
                        'question': question.get_text().strip(),
                        'answer': answer.get_text().strip()
                    })
                    
        except Exception as e:
            self.logger.error(f"Error extracting FAQs: {e}")
        return faqs

    def _extract_support_info(self, soup) -> Dict:
        support = {}
        try:
            # Find support channels
            support_elements = soup.find_all(['div', 'section'], 
                class_=lambda x: x and ('support' in x.lower() or 'help' in x.lower()))
            
            if support_elements:
                support['channels'] = [elem.get_text().strip() for elem in support_elements]
            
            # Find business hours
            hours_elem = soup.find(class_=lambda x: x and ('hours' in x.lower() or 'schedule' in x.lower()))
            if hours_elem:
                support['hours'] = hours_elem.get_text().strip()
                
        except Exception as e:
            self.logger.error(f"Error extracting support info: {e}")
        return support

class SmartBot:
    def __init__(self, website_data: Dict):
        self.data = website_data
        self.conversation_history = []
        self.logger = logging.getLogger(__name__)

    # [Your existing SmartBot methods remain the same]
    def get_response(self, query: str) -> str:
        """Generate response based on website data"""
        query = query.lower()
        
        # Handle different types of queries
        if any(word in query for word in ['product', 'service', 'price']):
            return self._handle_product_query()
        elif any(word in query for word in ['contact', 'email', 'phone']):
            return self._handle_contact_query()
        elif any(word in query for word in ['faq', 'question']):
            return self._handle_faq_query()
        elif any(word in query for word in ['support', 'help']):
            return self._handle_support_query()
        else:
            return self._handle_general_query()

    def _handle_product_query(self) -> str:
        if not self.data.get('products'):
            return "I'm sorry, I don't have product information available."
        
        response = "Here are our products:\n\n"
        for product in self.data['products']:
            response += f"• {product.get('name', 'Unknown Product')}\n"
            if product.get('description'):
                response += f"  Description: {product['description']}\n"
            if product.get('price'):
                response += f"  Price: {product['price']}\n"
            response += "\n"
        return response

    def _handle_contact_query(self) -> str:
        contact = self.data.get('contact', {})
        if not contact:
            return "I'm sorry, I don't have contact information available."
        
        response = "Here's our contact information:\n\n"
        if contact.get('email'):
            response += f"Email: {contact['email']}\n"
        if contact.get('phone'):
            response += f"Phone: {contact['phone']}\n"
        if contact.get('address'):
            response += f"Address: {contact['address']}\n"
        return response

    def _handle_faq_query(self) -> str:
        if not self.data.get('faqs'):
            return "I'm sorry, I don't have FAQ information available."
        
        response = "Here are some frequently asked questions:\n\n"
        for faq in self.data['faqs']:
            response += f"Q: {faq['question']}\n"
            response += f"A: {faq['answer']}\n\n"
        return response

    def _handle_support_query(self) -> str:
        support = self.data.get('support', {})
        if not support:
            return "I'm sorry, I don't have support information available."
        
        response = "Support Information:\n\n"
        if support.get('hours'):
            response += f"Hours: {support['hours']}\n"
        if support.get('channels'):
            response += "Support Channels:\n"
            for channel in support['channels']:
                response += f"• {channel}\n"
        return response

    def _handle_general_query(self) -> str:
        company = self.data.get('company_info', {})
        response = f"Welcome to {company.get('name', 'our company')}!\n\n"
        if company.get('description'):
            response += f"{company['description']}\n\n"
        response += "I can help you with:\n"
        response += "• Product information\n"
        response += "• Contact details\n"
        response += "• FAQs\n"
        response += "• Support information\n\n"
        response += "What would you like to know about?"
        return response

async def main():
    try:
        print("Starting the chatbot...")
        website_url = input("Enter website URL to analyze: ")
        print(f"\nAnalyzing website: {website_url}")
        
        analyzer = WebsiteAnalyzer(website_url)
        website_data = analyzer.analyze()
        
        # Save the scraped data for debugging
        try:
            with open('website_data.json', 'w') as f:
                json.dump(website_data, f, indent=4)
            print("Debug data saved successfully")
        except IOError as e:
            print(f"Warning: Could not save debug data: {e}")
        
        bot = SmartBot(website_data)
        print("\nBot is ready! Type 'exit' to quit.")
        
        while True:
            try:
                query = input("\nYou: ").strip()
                if query.lower() == 'exit':
                    print("Goodbye!")
                    break
                    
                response = bot.get_response(query)
                print(f"\nBot: {response}")
            except KeyboardInterrupt:
                print("\nBot shutting down...")
                break
            except Exception as e:
                print(f"\nAn error occurred while processing your input: {e}")
                
    except Exception as e:
        print(f"An error occurred while starting the bot: {e}")
        logger.error(f"Bot startup error: {e}")

if __name__ == "__main__":
    asyncio.run(main())