import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import json
from datetime import datetime

# Load the token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Enable ALL intents
intents = discord.Intents.all()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

class CustomerServiceBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.active_tickets = {}
        self.setup_commands()
        self.support_categories = {
            "technical": "🔧 Technical Support",
            "billing": "💰 Billing Support",
            "product": "📦 Product Information",
            "account": "👤 Account Help",
            "general": "❓ General Inquiry"
        }

    async def setup_hook(self):
        print(f"Logged in as {self.user}")
        print("Bot is ready to handle customer service!")
        await self.tree.sync()

    def setup_commands(self):
        @self.command(name='support')
        async def support(ctx):
            embed = discord.Embed(
                title="Customer Support Center",
                description="How can we assist you today?",
                color=discord.Color.blue()
            )
            
            # Add category fields
            for emoji, category in self.support_categories.items():
                embed.add_field(
                    name=category,
                    value=f"React with {emoji} for {category.split(' ', 1)[1]}",
                    inline=False
                )
            
            # Add contact information
            embed.add_field(
                name="📞 Direct Contact",
                value="Email: support@example.com\nPhone: 1-800-SUPPORT",
                inline=False
            )
            
            # Add footer with operating hours
            embed.set_footer(text="Support Hours: 24/7 | Response Time: Within 1 hour")
            
            message = await ctx.send(embed=embed)
            
            # Add reactions
            for emoji in self.support_categories.keys():
                await message.add_reaction(emoji)

        @self.command(name='ticket')
        async def create_ticket(ctx, *, issue: str = None):
            ticket_id = f"TICKET-{len(self.active_tickets) + 1}"
            
            embed = discord.Embed(
                title=f"Support Ticket: {ticket_id}",
                description="Your support ticket has been created.",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="Issue Description",
                value=issue if issue else "No description provided",
                inline=False
            )
            
            embed.add_field(
                name="Status",
                value="🟢 Open",
                inline=True
            )
            
            embed.add_field(
                name="Priority",
                value="⚪ To be assessed",
                inline=True
            )
            
            embed.set_footer(text=f"Submitted by {ctx.author.name}")
            
            ticket_message = await ctx.send(embed=embed)
            self.active_tickets[ticket_id] = {
                "user": ctx.author.id,
                "message_id": ticket_message.id,
                "status": "open",
                "priority": "normal",
                "created_at": datetime.utcnow(),
                "issue": issue
            }
            
            # Add ticket management reactions
            await ticket_message.add_reaction("🔄")  # Update status
            await ticket_message.add_reaction("⬆️")  # Increase priority
            await ticket_message.add_reaction("⬇️")  # Decrease priority
            await ticket_message.add_reaction("✅")  # Close ticket

        @self.command(name='faq')
        async def show_faq(ctx):
            embed = discord.Embed(
                title="Frequently Asked Questions",
                description="Here are some common questions and answers:",
                color=discord.Color.blue()
            )
            
            faqs = {
                "How do I reset my password?": 
                    "Go to the login page and click 'Forgot Password'. Follow the email instructions.",
                "Where can I find pricing information?": 
                    "Visit our pricing page at example.com/pricing or type !pricing for details.",
                "How do I contact support?": 
                    "Email support@example.com or create a ticket using !ticket command.",
                "What are your business hours?": 
                    "We provide 24/7 support with priority handling during business hours (9 AM - 5 PM EST)."
            }
            
            for question, answer in faqs.items():
                embed.add_field(name=question, value=answer, inline=False)
            
            await ctx.send(embed=embed)

        @self.command(name='status')
        async def check_status(ctx):
            embed = discord.Embed(
                title="System Status",
                description="Current system status and response times:",
                color=discord.Color.green()
            )
            
            statuses = {
                "Website": "🟢 Operational",
                "API": "🟢 Operational",
                "Database": "🟢 Operational",
                "Support": "🟢 Available"
            }
            
            for system, status in statuses.items():
                embed.add_field(name=system, value=status, inline=True)
            
            embed.add_field(
                name="Response Times",
                value="• Chat: < 5 minutes\n• Email: < 1 hour\n• Tickets: < 4 hours",
                inline=False
            )
            
            await ctx.send(embed=embed)

        @self.event
        async def on_reaction_add(reaction, user):
            if user == self.user:
                return

            message = reaction.message
            emoji = str(reaction.emoji)

            # Handle support category reactions
            if emoji in self.support_categories:
                await self.handle_support_reaction(message.channel, user, emoji)
            
            # Handle ticket management reactions
            elif message.id in [ticket["message_id"] for ticket in self.active_tickets.values()]:
                await self.handle_ticket_reaction(message, user, emoji)

    async def handle_support_reaction(self, channel, user, category):
        responses = {
            "technical": {
                "title": "Technical Support",
                "description": "Let's resolve your technical issue.",
                "color": discord.Color.green(),
                "fields": [
                    ("Common Solutions", "• Check our documentation\n• Clear your cache\n• Update your browser"),
                    ("Contact Support", "Email: tech@example.com\nPhone: 1-800-TECH")
                ]
            },
            "billing": {
                "title": "Billing Support",
                "description": "Let's help with your billing inquiry.",
                "color": discord.Color.gold(),
                "fields": [
                    ("Billing Options", "• View current plan\n• Update payment method\n• Request refund"),
                    ("Contact Billing", "Email: billing@example.com")
                ]
            },
            "product": {
                "title": "Product Information",
                "description": "Here's information about our products.",
                "color": discord.Color.blue(),
                "fields": [
                    ("Available Plans", "• Basic: $10/month\n• Pro: $25/month\n• Enterprise: Custom"),
                    ("Features", "• Cloud Storage\n• 24/7 Support\n• API Access")
                ]
            }
        }

        response = responses.get(category, {
            "title": "General Support",
            "description": "How can we help you today?",
            "color": discord.Color.blue(),
            "fields": [
                ("Support Options", "• Browse FAQ (!faq)\n• Create ticket (!ticket)\n• Contact support"),
                ("Contact Us", "Email: support@example.com")
            ]
        })

        embed = discord.Embed(
            title=response["title"],
            description=response["description"],
            color=response["color"]
        )

        for name, value in response["fields"]:
            embed.add_field(name=name, value=value, inline=False)

        embed.set_footer(text=f"Support ticket created for {user.name}")
        await channel.send(embed=embed)

    async def handle_ticket_reaction(self, message, user, emoji):
        # Update ticket status based on reaction
        for ticket_id, ticket in self.active_tickets.items():
            if ticket["message_id"] == message.id:
                if emoji == "✅":
                    ticket["status"] = "closed"
                elif emoji == "⬆️":
                    ticket["priority"] = "high"
                elif emoji == "⬇️":
                    ticket["priority"] = "low"
                
                # Update ticket message
                embed = message.embeds[0]
                embed.set_field_at(
                    1,
                    name="Status",
                    value=f"{'🟢' if ticket['status'] == 'open' else '🔴'} {ticket['status'].capitalize()}",
                    inline=True
                )
                embed.set_field_at(
                    2,
                    name="Priority",
                    value=f"{'🔴' if ticket['priority'] == 'high' else '🟡' if ticket['priority'] == 'normal' else '🟢'} {ticket['priority'].capitalize()}",
                    inline=True
                )
                
                await message.edit(embed=embed)
                break

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} servers')

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.name}!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # This line is crucial for commands to work!
    await bot.process_commands(message)

    if 'hello' in message.content.lower():
        await message.channel.send('Hey there!')

def run_bot():
    bot = CustomerServiceBot()
    bot.run(TOKEN)

if __name__ == "__main__":
    run_bot()
    