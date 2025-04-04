import discord
from typing import Dict, List, Any

class ResponseFormatter:
    def __init__(self):
        self.templates = {
            'product_inquiry': {
                'color': discord.Color.blue(),
                'emoji': '📦',
                'title': 'Product Information'
            },
            'support': {
                'color': discord.Color.green(),
                'emoji': '🔧',
                'title': 'Technical Support'
            },
            'account': {
                'color': discord.Color.purple(),
                'emoji': '👤',
                'title': 'Account Management'
            },
            'billing': {
                'color': discord.Color.gold(),
                'emoji': '💰',
                'title': 'Billing Information'
            },
            'general': {
                'color': discord.Color.blue(),
                'emoji': 'ℹ️',
                'title': 'Information'
            }
        }

    def format_response(self, response_data: Dict, intent: str) -> discord.Embed:
        """Format response into a Discord embed"""
        template = self.templates.get(intent, self.templates['general'])
        
        embed = discord.Embed(
            title=f"{template['emoji']} {template['title']}",
            color=template['color']
        )

        # Add main response
        if response_data.get('main_response'):
            embed.description = response_data['main_response']

        # Add additional fields
        if response_data.get('details'):
            for title, content in response_data['details'].items():
                embed.add_field(
                    name=title,
                    value=content,
                    inline=False
                )

        # Add follow-up suggestions if present
        if response_data.get('suggestions'):
            embed.add_field(
                name="📝 Additional Information",
                value="\n".join(f"• {suggestion}" for suggestion in response_data['suggestions']),
                inline=False
            )

        # Add footer
        embed.set_footer(text="How else can I assist you?")

        return embed

    def format_error(self, error_message: str) -> discord.Embed:
        """Format error messages"""
        embed = discord.Embed(
            title="⚠️ Error",
            description=error_message,
            color=discord.Color.red()
        )
        return embed

    def format_loading(self) -> discord.Embed:
        """Format loading message"""
        embed = discord.Embed(
            title="⏳ Processing",
            description="Let me help you with that...",
            color=discord.Color.light_grey()
        )
        return embed