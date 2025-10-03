# cogs/researcher.py
from discord.ext import commands
from discord import app_commands
import discord
import tools.llm_agent as agent
import ast

class Researcher(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ask", description="Ask a question")
    async def ask(self, interaction: discord.Interaction, query: str):
        # Prevent timing out
        await interaction.response.defer()

        # Run the agent query and await a response.
        for response in agent.query(query):
            print(response)
            if response.get("agentResponse") is not None:
                r = response["agentResponse"]["messages"][-1].content.strip()
                if r != "":
                    embed = discord.Embed(
                        title=query.strip(),
                        description="",
                        color=discord.Color.blue()
                    )
                    embed.add_field(name="", value=r, inline=True)
                    await interaction.followup.send(embed=embed, ephemeral=True)
            elif response.get("toolResponse") is not None:
                url_string = ""
                l = ast.literal_eval(response["toolResponse"]["messages"][-1].content)
                for site in l:
                    url_string += site["url"] + ", "
                if url_string is not None:
                    embed = discord.Embed(
                        title="Searched",
                        description="",
                        color=discord.Color.blurple()
                    )
                    embed.add_field(name="", value=url_string[:-2], inline=True)
                    await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Researcher(bot))
