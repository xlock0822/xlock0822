import os
from dotenv import load_dotenv

def verify_setup():
    # Print current directory
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")

    # Print all files in directory
    print("\nFiles in directory:")
    files = os.listdir()
    for file in files:
        print(f"- {file}")

    # Check if .env exists
    env_exists = os.path.exists('.env')
    print(f"\n.env file exists: {env_exists}")

    # Load and check token
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    print(f"\nToken status:")
    print(f"Token found: {'Yes' if token else 'No'}")
    if token:
        print(f"Token length: {len(token)}")
        print(f"Token starts with: {token[:10]}...")
    
    return token is not None

if __name__ == "__main__":
    try:
        is_valid = verify_setup()
        if not is_valid:
            print("\nPlease check your .env file and token!")
    except Exception as e:
        print(f"\nError occurred: {str(e)}")