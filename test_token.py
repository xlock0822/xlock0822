import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
print(f"Token found: {'Yes' if token else 'No'}")
print(f"Token length: {len(token) if token else 'N/A'}")