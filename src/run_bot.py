from dotenv import load_dotenv
from discord_bot import start_bot
import os

def main():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # Load .env file
    env_path = os.path.join(project_root, '.env')
    load_dotenv(env_path)
    
    # Start the bot
    print("Starting bot...")
    start_bot()

if __name__ == "__main__":
    main()