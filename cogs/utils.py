# cogs/utils.py
from discord.ext import commands
from discord import app_commands
import discord
import time

class Utils(commands.Cog):
    """
    A cog for utility commands.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = time.time()

    @app_commands.command(name="ping", description="Shows the bot's latency.")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)  # Latency in milliseconds
        await interaction.response.send_message(f"Pong! Latency is {latency}ms.")

    @app_commands.command(name="serverinfo", description="Displays information about the server.")
    async def serverinfo(self, interaction: discord.Interaction):
        server = interaction.guild
        if not server:
            await interaction.response.send_message("This command can only be used in a server.")
            return

        # Create an embed for a richer display
        embed = discord.Embed(
            title=f"Server Info: {server.name}",
            description=f"Here is some information about **{server.name}**.",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=server.icon.url if server.icon else None)
        embed.add_field(name="Server ID", value=server.id, inline=True)
        embed.add_field(name="Owner", value=server.owner.mention, inline=True)
        embed.add_field(name="Members", value=server.member_count, inline=True)
        embed.add_field(name="Text Channels", value=len(server.text_channels), inline=True)
        embed.add_field(name="Voice Channels", value=len(server.voice_channels), inline=True)
        embed.add_field(name="Roles", value=len(server.roles), inline=True)
        embed.add_field(name="Created At", value=server.created_at.strftime("%b %d, %Y"), inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="uptime", description="Shows how long the bot has been online.")
    async def uptime(self, interaction: discord.Interaction):
        current_time = time.time()
        uptime_seconds = int(round(current_time - self.start_time))
        
        # Format the uptime into a human-readable string
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        uptime_str = ""
        if days > 0:
            uptime_str += f"{days}d "
        if hours > 0:
            uptime_str += f"{hours}h "
        if minutes > 0:
            uptime_str += f"{minutes}m "
        uptime_str += f"{seconds}s"

        await interaction.response.send_message(f"I have been online for: **{uptime_str}**")

async def setup(bot: commands.Bot):
    await bot.add_cog(Utils(bot))
