# bot.py
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from tools.message_flagging import flag_message
from profanity_check import predict_prob
from discord.ext import commands
from dotenv import load_dotenv
import language_tool_python
import asyncio
import discord
import os

# Constants
PROFANE           = 0
AVERAGE_SENTIMENT = 1

# Load environment variables from a .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set intents
intents                 = discord.Intents.default()
intents.message_content = True 
intents.members         = True

# Load the VADER sentiment analyzer and NLTK stuff
sentiment_analyzer = SentimentIntensityAnalyzer()
grammar_tool       = language_tool_python.LanguageTool('en-US') 
dictionary         = set([line.strip().lower() for line in open('data/words.txt').readlines()]).union(set([line.strip().lower() for line in open('data/stupid_words.txt').readlines()]))

# We only use slash commands, but defining a command prefix is best practice
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

    # Sync all slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_message(message : discord.Message):
    # Simplify message for ease of analysis
    cleaned_message = "".join([c for c in message.content.strip().lower() if c.isalpha() or c == ' '])

    # Use profanity-check's analysis feature to determine profanity and the chance of this message being offsensive
    profanity_chance = predict_prob([cleaned_message])[0]
    print(profanity_chance)

    # Profanity chance threshold automatically triggers a message warning
    if profanity_chance > 0.8:
        await flag_message(message, PROFANE)
        return

    # Scan message for intent
    sentiment_scores = sentiment_analyzer.polarity_scores(cleaned_message)
    average_intent = sentiment_scores['compound']
    print(average_intent)
    
    # Inverse sentiment (higher is worse)
    inv_sentiment = 1 - ((average_intent + 1) / 2)
    average_prof_inv = (profanity_chance + inv_sentiment) / 2
    print(average_prof_inv)

    if average_prof_inv > 0.6:
        await flag_message(message, AVERAGE_SENTIMENT)

# Context menus cannot be inside classes

@bot.tree.context_menu(name="Message analysis")
async def messageanalysis(interaction: discord.Interaction, message: discord.Message):
    msg = "".join([c for c in message.content.strip().lower() if c.isalpha() or c == ' '])
    if not len(msg.strip()):
        return

    # Analyze sentiment scores
    scores = sentiment_analyzer.polarity_scores(msg)
    
    # Analyze word spelling accuracy
    score = 0
    tot   = 0
    for word in msg.split(' '):
        if not len(word.strip()):
            continue
        if word.strip() in dictionary:
            score += 1
        tot += 1
    score /= tot
    
    # Analyze grammar
    matches = grammar_tool.check(message.content.strip())
    num_errors = len(matches)

    # Subtract all spelling errors, we dont count these
    for error in matches:
        if error.ruleId == "MORFOLOGIK_RULE_EN_US":
            num_errors -= 1

    embed = discord.Embed(
        title=f"Message analysis",
        description=f"Message analysis for {message.author.mention}",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=None)
    embed.add_field(name="Message sentiment", value=scores["compound"], inline=True)
    embed.add_field(name="Spelling", value=f"{round(score * 100, 1)}%", inline=True)
    embed.add_field(name="Grammar", value=f"{num_errors} errors ({round(100 * num_errors / tot)}%)")

    await interaction.response.send_message(embed=embed)

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                # The cog name is the filename without the .py extension.
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded cog: {filename[:-3]}')
            except Exception as e:
                print(f'Failed to load cog {filename[:-3]}: {e}')

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
