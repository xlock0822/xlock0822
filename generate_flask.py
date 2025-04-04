import os
import secrets

# Generate a secure key
secret_key = secrets.token_hex(32)  # This generates a 64-character hex string

print("\n=== Generated Flask Secret Key ===")
print(f"\nNew secret key: {secret_key}")
print("\nCopy this key and update your .env file!")
print("\nExample .env format:")
print(f"DISCORD_TOKEN={os.getenv('DISCORD_TOKEN')}")
print(f"FLASK_SECRET_KEY={secret_key}")
print("OPENAI_API_KEY=your-openai-api-key")
print("FLASK_DEBUG=True")
print("PORT=5000")