import asyncio
import requests
from urllib.parse import urlparse
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SiteIntegrator:
    def __init__(self, url):
        self.url = self._format_url(url)
        self.data = {}
        
    def _format_url(self, url):
        """Ensure URL has proper format"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    async def run_integration(self):
        logger.info(f"\n=== Starting Integration for {self.url} ===\n")
        
        try:
            # Step 1: Verify site accessibility
            logger.info("Step 1: Verifying site accessibility...")
            if not self._verify_site():
                raise Exception("Site not accessible")
            logger.info("✅ Site accessible")

            # Step 2: Extract site content
            logger.info("\nStep 2: Extracting site content...")
            content = self._get_site_content()
            if content:
                logger.info("✅ Content extracted")
            
            # Step 3: Parse information
            logger.info("\nStep 3: Parsing site information...")
            self.data = self._parse_information(content)
            logger.info("✅ Information parsed")
            
            # Step 4: Verify data
            logger.info("\nStep 4: Verifying extracted data...")
            self._verify_data()
            logger.info("✅ Data verified")
            
            # Step 5: Format results
            logger.info("\nStep 5: Formatting results...")
            results = self._format_results()
            logger.info("✅ Results formatted")
            
            logger.info("\n=== Integration Complete ===")
            logger.info("\nExtracted Information:")
            self._print_results(results)
            
            return results
            
        except Exception as e:
            logger.error(f"\n❌ Integration failed: {str(e)}")
            return None
    
    def _verify_site(self):
        """Verify site is accessible"""
        try:
            response = requests.get(self.url)
            return response.status_code == 200
        except:
            return False
    
    def _get_site_content(self):
        """Get site content"""
        try:
            response = requests.get(self.url)
            return response.text
        except:
            return None
    
    def _parse_information(self, content):
        """Parse site information"""
        if not content:
            return {}
            
        # Basic information extraction
        data = {
            'url': self.url,
            'timestamp': datetime.now().isoformat(),
            'content_length': len(content),
            'sections_found': self._identify_sections(content)
        }
        
        return data
    
    def _identify_sections(self, content):
        """Identify main sections of the site"""
        sections = []
        keywords = ['about', 'contact', 'product', 'service', 'support']
        
        content_lower = content.lower()
        for keyword in keywords:
            if keyword in content_lower:
                sections.append(keyword)
        
        return sections
    
    def _verify_data(self):
        """Verify extracted data"""
        required_fields = ['url', 'timestamp', 'content_length']
        for field in required_fields:
            if field not in self.data:
                raise Exception(f"Missing required field: {field}")
    
    def _format_results(self):
        """Format integration results"""
        return {
            'site_info': {
                'url': self.url,
                'integrated_at': self.data.get('timestamp'),
                'sections_found': self.data.get('sections_found', [])
            },
            'content_stats': {
                'content_length': self.data.get('content_length', 0),
                'sections_count': len(self.data.get('sections_found', []))
            },
            'status': 'success'
        }
    
    def _print_results(self, results):
        """Print formatted results"""
        print("\n=== Integration Results ===")
        print(f"\nSite Information:")
        print(f"URL: {results['site_info']['url']}")
        print(f"Integrated At: {results['site_info']['integrated_at']}")
        print(f"Sections Found: {', '.join(results['site_info']['sections_found'])}")
        
        print(f"\nContent Statistics:")
        print(f"Content Length: {results['content_stats']['content_length']} characters")
        print(f"Sections Count: {results['content_stats']['sections_count']}")
        
        print(f"\nStatus: {results['status']}")

async def main():
    # Your Netlify site
    url = "deluxe-concha-eb7972.netlify.app"
    
    # Create integrator
    integrator = SiteIntegrator(url)
    
    # Run integration
    results = await integrator.run_integration()
    
    if results:
        logger.info("\n✅ Integration successful!")
    else:
        logger.error("\n❌ Integration failed!")

if __name__ == "__main__":
    asyncio.run(main())