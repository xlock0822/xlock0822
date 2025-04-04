import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load the token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up logging
import logging
logging.basicConfig(level=logging.INFO)

# Create bot instance with required intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print('Connected to:')
    for guild in bot.guilds:
        print(f'- {guild.name} (id: {guild.id})')

@bot.command(name='test')
async def test(ctx):
    await ctx.send('Bot is working!')

# Run the bot
print(f"Token prefix: {TOKEN[:10]}...") # This will show just the start of your token
bot.run(TOKEN)