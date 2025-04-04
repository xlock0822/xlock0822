import os
from dotenv import load_dotenv

def debug_token():
    # Get absolute path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, '.env')
    
    print(f"Looking for .env file at: {env_path}")
    print(f"File exists: {os.path.exists(env_path)}")
    
    # Load token
    load_dotenv(env_path)
    token = os.getenv('DISCORD_TOKEN')
    
    # Debug info
    print("\nToken Debug Info:")
    print(f"Token found: {'Yes' if token else 'No'}")
    if token:
        print(f"Token length: {len(token)}")
        print(f"Token format check: {'.' in token}")
        print(f"First few characters: {token[:10]}...")
    else:
        print("No token found in .env file")

if __name__ == "__main__":
    debug_token()