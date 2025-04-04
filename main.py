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
from web_integrator import WebIntegrator
from website_integrator import CompanyDataIntegrator
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

# Initialize Flask app - KEEP ONLY ONE INSTANCE
app = Flask(__name__)
CORS(app, origins=[
    "http://your-shopify-store.myshopify.com",  # Replace with your actual Shopify store URL
    "https://deluxe-concha-eb7972.netlify.app"
])

web_integrator = WebIntegrator(app)

# Shopify customer service routes
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
        return "We offer free shipping on orders over $50. Standard shipping takes 3-5 business days."
    elif 'return' in message:
        return "Our return policy allows returns within 30 days of purchase. Items must be unused with original tags."
    elif 'order' in message:
        return "To check your order status, please provide your order number."
    else:
        return "How can I help you with your shopping today? I can assist with shipping, returns, orders, and product information."

# Website integration routes
@app.route('/setup', methods=['GET'])
def setup_page():
    return render_template('setup.html')

@app.route('/setup/integrate', methods=['POST'])
async def integrate_website():
    data = request.json
    website_url = data.get('website_url')
    
    if not website_url:
        return jsonify({'error': 'Website URL is required'}), 400
        
    try:
        integrator = CompanyDataIntegrator(
            website_url=website_url,
            google_api_key=os.getenv('GOOGLE_API_KEY')
        )
        
        company_data = await integrator.integrate()
        
        return jsonify({
            'status': 'success',
            'message': 'Integration complete',
            'data': company_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Keep your WebsiteAnalyzer and CustomerServiceBot classes as they are

if __name__ == '__main__':
    # Check if running in command-line mode or web server mode
    if len(sys.argv) > 1:
        # Command-line mode
        parser = argparse.ArgumentParser(description='Customer Service Bot')
        parser.add_argument('--url', type=str, help='Website URL to analyze')
        args = parser.parse_args()

        if not args.url:
            print("Please provide a website URL with --url parameter")
            sys.exit(1)

        try:
            print(f"\nAnalyzing website: {args.url}")
            asyncio.run(main())
        except Exception as e:
            logger.error(f"Error in main: {str(e)}")
            print("\nAn error occurred while initializing the bot.")
            sys.exit(1)
    else:
        # Web server mode
        app.run(debug=True, port=5001)
