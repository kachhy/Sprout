# cogs/games.py
from discord.ext import commands
from discord import app_commands
import discord
import time

class Games(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

async def setup(bot: commands.Bot):
    await bot.add_cog(Games(bot))
