import asyncio
from typing import Dict, Optional, List
import argparse
import sys
import logging
from datetime import datetime
import json
import os
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=[
    "http://dualitymade.com",
    "https://dualitymade.com",
    "https://deluxe-concha-eb7972.netlify.app"
])

class WebsiteAnalyzer:
    def __init__(self, url: str):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    async def analyze(self) -> Dict:
        try:
            logger.info(f"Analyzing website: {self.url}")
            response = requests.get(self.url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            data = {
                'company_info': self._extract_company_info(soup),
                'products': self._extract_products(soup),
                'support': self._extract_support_info(soup),
                'contact': self._extract_contact_info(soup),
                'faqs': self._extract_faqs(soup)
            }
            
            logger.info("Website analysis completed successfully")
            return data
        except Exception as e:
            logger.error(f"Error analyzing website: {str(e)}")
            return {}

    def _extract_company_info(self, soup) -> Dict:
        return {
            'name': self._find_company_name(soup),
            'description': self._find_meta_description(soup),
            'domain': urlparse(self.url).netloc
        }

    def _extract_products(self, soup) -> List:
        products = []
        product_elements = soup.find_all(class_=lambda x: x and 'product' in x.lower())
        
        for element in product_elements[:5]:
            products.append({
                'name': element.get_text().strip()[:100],
                'description': self._find_nearby_description(element)
            })
        
        return products

    def _extract_support_info(self, soup) -> Dict:
        support_info = {
            'email': self._find_emails(soup),
            'phone': self._find_phones(soup),
            'hours': self._find_business_hours(soup)
        }
        return support_info

    def _extract_contact_info(self, soup) -> Dict:
        return {
            'email': self._find_emails(soup),
            'phone': self._find_phones(soup),
            'address': self._find_address(soup)
        }

    def _extract_faqs(self, soup) -> List:
        faqs = []
        faq_elements = soup.find_all(class_=lambda x: x and 'faq' in x.lower())
        
        for element in faq_elements:
            question = element.find(class_=lambda x: x and 'question' in x.lower())
            answer = element.find(class_=lambda x: x and 'answer' in x.lower())
            
            if question and answer:
                faqs.append({
                    'question': question.get_text().strip(),
                    'answer': answer.get_text().strip()
                })
        
        return faqs

    def _find_company_name(self, soup) -> str:
        title = soup.find('title')
        if title:
            return title.get_text().split('|')[0].strip()
        return urlparse(self.url).netloc

    def _find_meta_description(self, soup) -> str:
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta:
            return meta.get('content', '')
        return ''

    def _find_nearby_description(self, element) -> str:
        desc = element.find_next(class_=lambda x: x and 'description' in x.lower())
        if desc:
            return desc.get_text().strip()[:200]
        return ''

    def _find_emails(self, soup) -> List[str]:
        import re
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return list(set(re.findall(email_pattern, str(soup))))

    def _find_phones(self, soup) -> List[str]:
        import re
        phone_pattern = r'\+?1?\d{9,15}'
        return list(set(re.findall(phone_pattern, str(soup))))

    def _find_business_hours(self, soup) -> str:
        hours_element = soup.find(class_=lambda x: x and 'hours' in x.lower())
        if hours_element:
            return hours_element.get_text().strip()
        return "24/7"

    def _find_address(self, soup) -> str:
        address_element = soup.find(class_=lambda x: x and 'address' in x.lower())
        if address_element:
            return address_element.get_text().strip()
        return ""

# Flask routes
@app.route('/shopify-support')
def shopify_support():
    return render_template('shopify_chat.html')

@app.route('/api/shopify-chat', methods=['POST'])
def handle_shopify_chat():
    data = request.json
    user_message = data.get('message', '')
    
    response = generate_shopify_response(user_message)
    
    return jsonify({'response': response})

def generate_shopify_response(message):
    message = message.lower()
    if 'shipping' in message:
        return "We offer free shipping on orders over $100. Standard shipping takes 3-5 business days."
    elif 'return' in message or 'refund' in message:
        return "Our return policy allows returns within 30 days of purchase. Items must be unused with original tags. Please email support@dualitymade.com to initiate a return."
    elif 'order' in message or 'tracking' in message:
        return "To check your order status, please email support@dualitymade.com with your order number."
    elif 'contact' in message:
        return "You can reach us at support@dualitymade.com for any questions or concerns."
    elif 'product' in message or 'items' in message:
        return "We offer a variety of high-quality clothing items. You can view our full collection on our website. For specific product questions, please email support@dualitymade.com"
    else:
        return "How can I help you with your shopping today? I can assist with shipping, returns, orders, and product information. For specific questions, please email support@dualitymade.com"

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)