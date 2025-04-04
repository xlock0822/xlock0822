import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Create bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is connected as {bot.user}')
    print('Connected to these servers:')
    for guild in bot.guilds:
        print(f'- {guild.name}')

@bot.event
async def on_message(message):
    # Don't respond to bot's own messages
    if message.author == bot.user:
        return

    # Process commands
    await bot.process_commands(message)

    # Respond to mentions
    if bot.user.mentioned_in(message):
        await message.channel.send(f'Hello {message.author.name}! How can I help you?')

@bot.command(name='test')
async def test(ctx):
    await ctx.send('Bot is working!')

# Run the bot
bot.run(TOKEN)