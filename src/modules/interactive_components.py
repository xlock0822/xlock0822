import discord
from discord.ui import View, Button, Select
from typing import List, Dict, Optional, Callable
import asyncio

class InteractiveMenu(View):
    def __init__(self, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.response = None

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

class ProductMenu(View):
    def __init__(self, products: Dict, callback: Callable):
        super().__init__(timeout=300)
        self.products = products
        self.callback = callback
        self._add_product_buttons()

    def _add_product_buttons(self):
        for product_id, product in self.products.items():
            button = Button(
                label=product['name'],
                style=discord.ButtonStyle.primary,
                custom_id=f"product_{product_id}"
            )
            button.callback = self._create_callback(product)
            self.add_item(button)

    def _create_callback(self, product: Dict):
        async def button_callback(interaction: discord.Interaction):
            await interaction.response.defer()
            await self.callback(interaction, product)
        return button_callback

class SupportMenu(View):
    def __init__(self, categories: List[Dict], callback: Callable):
        super().__init__(timeout=300)
        self.add_item(SupportCategorySelect(categories, callback))

class SupportCategorySelect(Select):
    def __init__(self, categories: List[Dict], callback: Callable):
        options = [
            discord.SelectOption(
                label=category['name'],
                description=category['description'][:100],
                value=category['id']
            )
            for category in categories
        ]
        super().__init__(
            placeholder="Choose a support category",
            options=options,
            min_values=1,
            max_values=1
        )
        self.callback_func = callback

    async def callback(self, interaction: discord.Interaction):
        await self.callback_func(interaction, self.values[0])

class FeedbackButtons(View):
    def __init__(self, feedback_callback: Callable):
        super().__init__(timeout=180)
        self.feedback_callback = feedback_callback
        self._add_feedback_buttons()

    def _add_feedback_buttons(self):
        reactions = [
            ("👍", "Helpful", discord.ButtonStyle.green),
            ("👎", "Not Helpful", discord.ButtonStyle.red),
            ("❓", "Need More Help", discord.ButtonStyle.blurple)
        ]
        
        for emoji, label, style in reactions:
            button = Button(
                emoji=emoji,
                label=label,
                style=style,
                custom_id=f"feedback_{label.lower().replace(' ', '_')}"
            )
            button.callback = self._create_feedback_callback(label)
            self.add_item(button)

    def _create_feedback_callback(self, feedback_type: str):
        async def button_callback(interaction: discord.Interaction):
            await self.feedback_callback(interaction, feedback_type)
        return button_callback

class ActionRow(View):
    def __init__(self, actions: List[Dict], callback: Callable):
        super().__init__(timeout=180)
        for action in actions:
            button = Button(
                label=action['label'],
                style=action.get('style', discord.ButtonStyle.secondary),
                emoji=action.get('emoji'),
                custom_id=f"action_{action['id']}"
            )
            button.callback = self._create_action_callback(action, callback)
            self.add_item(button)

    def _create_action_callback(self, action: Dict, callback: Callable):
        async def button_callback(interaction: discord.Interaction):
            await callback(interaction, action)
        return button_callback

class PaginatedEmbed:
    def __init__(
        self,
        pages: List[discord.Embed],
        timeout: int = 180
    ):
        self.pages = pages
        self.timeout = timeout
        self.current_page = 0
        self.view = self._create_view()

    def _create_view(self) -> View:
        view = View(timeout=self.timeout)
        
        # Previous page button
        prev_button = Button(
            emoji="⬅️",
            style=discord.ButtonStyle.grey,
            custom_id="prev_page"
        )
        prev_button.callback = self._prev_page
        
        # Next page button
        next_button = Button(
            emoji="➡️",
            style=discord.ButtonStyle.grey,
            custom_id="next_page"
        )
        next_button.callback = self._next_page
        
        view.add_item(prev_button)
        view.add_item(next_button)
        return view

    async def _prev_page(self, interaction: discord.Interaction):
        self.current_page = (self.current_page - 1) % len(self.pages)
        await self._update_page(interaction)

    async def _next_page(self, interaction: discord.Interaction):
        self.current_page = (self.current_page + 1) % len(self.pages)
        await self._update_page(interaction)

    async def _update_page(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            embed=self.pages[self.current_page],
            view=self.view
        )

    async def send(self, channel):
        self.message = await channel.send(
            embed=self.pages[0],
            view=self.view
        )
        return self.message

class TicketCreator(View):
    def __init__(self, callback: Callable):
        super().__init__(timeout=300)
        self.callback = callback
        self._add_buttons()

    def _add_buttons(self):
        categories = [
            ("Technical Support", "🔧", discord.ButtonStyle.primary),
            ("Billing Support", "💰", discord.ButtonStyle.green),
            ("Feature Request", "✨", discord.ButtonStyle.blurple),
            ("Bug Report", "🐛", discord.ButtonStyle.red)
        ]
        
        for label, emoji, style in categories:
            button = Button(
                label=label,
                emoji=emoji,
                style=style,
                custom_id=f"ticket_{label.lower().replace(' ', '_')}"
            )
            button.callback = self._create_ticket_callback(label)
            self.add_item(button)

    def _create_ticket_callback(self, category: str):
        async def button_callback(interaction: discord.Interaction):
            await self.callback(interaction, category)
        return button_callback

class QuickResponse(View):
    def __init__(self, options: List[str], callback: Callable):
        super().__init__(timeout=180)
        for i, option in enumerate(options):
            button = Button(
                label=option,
                style=discord.ButtonStyle.secondary,
                custom_id=f"quick_response_{i}"
            )
            button.callback = self._create_response_callback(option, callback)
            self.add_item(button)

    def _create_response_callback(self, option: str, callback: Callable):
        async def button_callback(interaction: discord.Interaction):
            await callback(interaction, option)
        return button_callback