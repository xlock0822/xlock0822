from content_processor import ContentProcessor
from response_generator import ResponseGenerator
import json
import os

async def integrate_site(url: str):
    print(f"\n=== Starting Site Integration for {url} ===")
    
    # Process content
    processor = ContentProcessor(url)
    processed_data = processor.process_content()
    
    if not processed_data:
        print("❌ Content processing failed")
        return False
    
    # Generate response templates
    generator = ResponseGenerator(processed_data)
    templates = generator.templates
    
    # Save integration results
    save_results(processed_data, templates)
    
    print("\n✅ Integration complete!")
    return True

def save_results(processed_data: dict, templates: dict):
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Save processed data
    with open('data/processed_content.json', 'w') as f:
        json.dump(processed_data, f, indent=2)
    
    # Save templates
    with open('data/response_templates.json', 'w') as f:
        json.dump(templates, f, indent=2)
    
    print("\n✅ Data saved successfully!")

if __name__ == "__main__":
    import asyncio
    url = "https://deluxe-concha-eb7972.netlify.app"
    asyncio.run(integrate_site(url))