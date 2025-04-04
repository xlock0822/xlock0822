from dotenv import load_dotenv
from discord_bot import start_bot

if __name__ == "__main__":
    load_dotenv()  # Load environment variables
    start_bot()