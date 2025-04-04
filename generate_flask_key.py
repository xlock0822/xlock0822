import secrets
from dotenv import load_dotenv
import os

def generate_and_show_key():
    # Load current .env
    load_dotenv()
    
    # Generate new secret key
    new_secret_key = secrets.token_hex(32)
    
    print("\n=== Generated Flask Secret Key ===")
    print(f"\nNew secret key: {new_secret_key}")
    
    # Show current .env content
    current_discord_token = os.getenv('DISCORD_TOKEN', 'your-discord-token')
    
    print("\nUpdate your .env file with:")
    print("------------------------")
    print(f"DISCORD_TOKEN={current_discord_token}")
    print(f"FLASK_SECRET_KEY={new_secret_key}")
    print("OPENAI_API_KEY=your-openai-api-key")
    print("FLASK_DEBUG=True")
    print("PORT=5000")
    print("------------------------")

if __name__ == "__main__":
    generate_and_show_key()