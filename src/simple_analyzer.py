import logging
from typing import Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time

class WebsiteAnalyzer:
    def __init__(self, url: str):
        self.url = url
        self.driver = None
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def setup_driver(self):
        try:
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            driver = uc.Chrome(options=options)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            self.logger.error(f"Failed to setup Chrome driver: {e}")
            raise

    def analyze(self) -> Dict:
        try:
            self.driver = self.setup_driver()
            self.logger.info(f"Analyzing website: {self.url}")
            
            self.driver.get(self.url)
            # Wait for content to load
            time.sleep(5)
            
            # Scroll to load dynamic content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            data = {
                'company_info': self._get_company_info(),
                'products': self._get_products(),
                'contact': self._get_contact_info(),
                'faqs': self._get_faqs(),
                'support': self._get_support_info()
            }
            
            return data
        except Exception as e:
            self.logger.error(f"Error analyzing website: {e}")
            return {}
        finally:
            if self.driver:
                self.driver.quit()

    def _get_company_info(self) -> Dict:
        try:
            # Get company name from meta tags or title
            company_name = self.driver.title
            description = ""
            
            # Try to get description from meta tags
            meta_selectors = [
                'meta[name="description"]',
                'meta[property="og:description"]',
                '[class*="description"]',
                '[class*="about"]'
            ]
            
            for selector in meta_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    description = element.get_attribute('content') or element.text
                    if description:
                        break
                except:
                    continue
            
            return {
                'name': company_name,
                'description': description
            }
        except Exception as e:
            self.logger.error(f"Error getting company info: {e}")
            return {}

    def _get_products(self) -> list:
        products = []
        try:
            # Wait for product elements to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="product"]'))
            )
            
            # Find product elements
            product_containers = self.driver.find_elements(
                By.CSS_SELECTOR, 
                '[class*="product-card"], [class*="product-item"], [class*="product"]'
            )
            
            for container in product_containers[:10]:  # Limit to first 10 products
                try:
                    product = {}
                    
                    # Try to get product name
                    try:
                        name = container.find_element(
                            By.CSS_SELECTOR, 
                            '[class*="name"], [class*="title"], h3'
                        ).text.strip()
                        product['name'] = name
                    except:
                        continue
                    
                    # Try to get product price
                    try:
                        price = container.find_element(
                            By.CSS_SELECTOR, 
                            '[class*="price"]'
                        ).text.strip()
                        product['price'] = price
                    except:
                        pass
                    
                    if product.get('name'):
                        products.append(product)
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error getting products: {e}")
        return products

    def _get_contact_info(self) -> Dict:
        contact_info = {}
        try:
            # Look for contact information in footer and contact sections
            contact_sections = self.driver.find_elements(
                By.CSS_SELECTOR,
                'footer, [class*="contact"], [class*="footer"]'
            )
            
            for section in contact_sections:
                # Look for phone numbers
                phone_patterns = ['tel:', 'phone:', 'call us']
                for pattern in phone_patterns:
                    try:
                        phone_element = section.find_element(
                            By.XPATH,
                            f".//*[contains(text(), '{pattern}')]"
                        )
                        contact_info['phone'] = phone_element.text.strip()
                        break
                    except:
                        continue
                
                # Look for email addresses
                try:
                    email_element = section.find_element(
                        By.CSS_SELECTOR,
                        'a[href^="mailto:"]'
                    )
                    contact_info['email'] = email_element.get_attribute('href').replace('mailto:', '')
                except:
                    pass
                
                # Look for address
                try:
                    address_element = section.find_element(
                        By.CSS_SELECTOR,
                        'address, [class*="address"]'
                    )
                    contact_info['address'] = address_element.text.strip()
                except:
                    pass
                
                if contact_info:
                    break
                    
        except Exception as e:
            self.logger.error(f"Error getting contact info: {e}")
        return contact_info

    def _get_faqs(self) -> list:
        faqs = []
        try:
            # Look for FAQ sections
            faq_sections = self.driver.find_elements(
                By.CSS_SELECTOR,
                '[class*="faq"], [class*="accordion"], [id*="faq"]'
            )
            
            for section in faq_sections:
                try:
                    # Find FAQ items
                    faq_items = section.find_elements(
                        By.CSS_SELECTOR,
                        '[class*="faq-item"], [class*="accordion-item"]'
                    )
                    
                    for item in faq_items:
                        try:
                            question = item.find_element(
                                By.CSS_SELECTOR,
                                '[class*="question"], [class*="header"], h3'
                            ).text.strip()
                            
                            answer = item.find_element(
                                By.CSS_SELECTOR,
                                '[class*="answer"], [class*="content"], p'
                            ).text.strip()
                            
                            if question and answer:
                                faqs.append({
                                    'question': question,
                                    'answer': answer
                                })
                        except:
                            continue
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error getting FAQs: {e}")
        return faqs

    def _get_support_info(self) -> Dict:
        support_info = {}
        try:
            # Look for support sections
            support_sections = self.driver.find_elements(
                By.CSS_SELECTOR,
                '[class*="support"], [class*="help"], [id*="support"]'
            )
            
            for section in support_sections:
                # Get support channels
                try:
                    channels = section.find_elements(
                        By.CSS_SELECTOR,
                        '[class*="channel"], [class*="option"], li'
                    )
                    if channels:
                        support_info['channels'] = [
                            channel.text.strip() 
                            for channel in channels 
                            if channel.text.strip()
                        ]
                except:
                    pass
                
                # Get support hours
                try:
                    hours_element = section.find_element(
                        By.CSS_SELECTOR,
                        '[class*="hours"], [class*="schedule"]'
                    )
                    support_info['hours'] = hours_element.text.strip()
                except:
                    pass
                
                if support_info:
                    break
                    
        except Exception as e:
            self.logger.error(f"Error getting support info: {e}")
        return support_info