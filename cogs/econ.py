# cogs/econ.py
from tools.econ_db import update_bank, update_cash, get_balance
from discord.ext import tasks, commands
from discord.ext import commands
from discord import app_commands, Embed
import discord
import asyncio

class Econ(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.tick.start()

    def cog_unload(self):
        self.daily_message.cancel()

    # Money injection tasks
    # Tick happens every hour
    @tasks.loop(hours=1)
    async def tick(self):
        print("tick")
        target_channel = None
        for guild in self.bot.guilds:
            # Update each user
            for member in guild.members:
                if not member.bot:
                    print(f"Updating balance for {member.id}")
                    update_bank(guild.id, member.id, 10)

            # Get the channel to send the update message in
            for channel in guild.text_channels:
                if 'general' in channel.name.lower():
                    if channel.permissions_for(guild.me).send_messages:
                        target_channel = channel
                        break
                    
        if target_channel:
            embed = Embed(
                title=f"Money!",
                description=f"Everyone in the server got $10.",
                color=discord.Color.brand_green()
            )
            await target_channel.send(embed=embed)

    @app_commands.command(name="balance", description="View your balance")
    async def balance(self, interaction: discord.Interaction):
        # Get user balance
        balance = get_balance(interaction.guild_id, interaction.user.id)

        embed = Embed(
            title=f"Account Summary",
            description=f"Balance for {interaction.user.display_name}",
            color=discord.Color.brand_green()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="💵 Cash", value="${}".format(balance["cash"]), inline=False)
        embed.add_field(name="🏦 Bank", value="${}".format(balance["bank"]), inline=False)

        await interaction.response.send_message(embed=embed)

    # Wait until the bot is ready before starting the loop
    @tick.before_loop
    async def before_tick(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(3600) # Wait one hour before starting


async def setup(bot: commands.Bot):
    await bot.add_cog(Econ(bot))