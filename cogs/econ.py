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
                title=f"Money 💰!",
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
        embed.add_field(name="💵 Cash", value="${:,.2f}".format(balance["cash"]), inline=False)
        embed.add_field(name="🏦 Bank", value="${:,.2f}".format(balance["bank"]), inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="send", description="Send cash to another user.")
    @app_commands.describe(member="The user you want to send money to.", amount="The amount of cash to send (must be > 0).")
    async def send_money(self, interaction: discord.Interaction, member: discord.Member, amount: app_commands.Range[float, 1]):
        server_id = str(interaction.guild_id)
        sender_id = str(interaction.user.id)
        recipient_id = str(member.id)
        rounded_amount = round(amount, 2)

        if sender_id == recipient_id:
            error_embed = discord.Embed(
                title="❌ Transaction Failed",
                description="You cannot send money to yourself!",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        if member.bot:
            error_embed = discord.Embed(
                title="❌ Transaction Failed",
                description="You cannot send money to a bot.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
        sender_balance = get_balance(server_id, sender_id)
        
        if sender_balance['bank'] < amount:
            error_embed = discord.Embed(
                title="❌ Transaction Failed",
                description=f"You only have **${sender_balance['bank']:,.2f}** in the bank, which is not enough to send **${rounded_amount:,.2f}**.",
                color=discord.Color.red()
            )
            # Send an ephemeral response so only the sender sees the error
            return await interaction.response.send_message(embed=error_embed, ephemeral=True)

        # Perform the transaction
        update_bank(server_id, sender_id, -rounded_amount)
        update_bank(server_id, recipient_id, rounded_amount)

        success_embed = discord.Embed(
            title="✅ Transaction Complete",
            description=f"You successfully sent **${rounded_amount:,.2f}** to {member.mention}!",
            color=discord.Color.green()
        )
        success_embed.set_thumbnail(url=member.display_avatar.url)
        success_embed.add_field(name="Your New Cash Balance", 
                                value=f"${sender_balance['bank'] - rounded_amount:,.2f}", 
                                inline=False)
        
        await interaction.response.send_message(embed=success_embed)

    # Wait until the bot is ready before starting the loop
    @tick.before_loop
    async def before_tick(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(3600) # Wait one hour before starting


async def setup(bot: commands.Bot):
    await bot.add_cog(Econ(bot))