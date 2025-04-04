from urllib.parse import urlparse
import requests

def test_url(url):
    # Add https if needed
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    print(f"Testing URL: {url}")
    
    try:
        # Parse URL
        parsed = urlparse(url)
        print(f"\nParsed URL components:")
        print(f"Scheme: {parsed.scheme}")
        print(f"Netloc: {parsed.netloc}")
        print(f"Path: {parsed.path}")
        
        # Test connection
        print("\nTesting connection...")
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        print(f"Response received: {'Yes' if response.text else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return False

# Test your URL
url = "deluxe-concha-eb7972.netlify.app"
test_url(url)