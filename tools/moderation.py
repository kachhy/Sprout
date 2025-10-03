# tools/moderation.py

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from tools.message_flagging import flag_message
from profanity_check import predict_prob
import discord

# Constants
PROFANE           = 0
AVERAGE_SENTIMENT = 1

sentiment_analyzer = SentimentIntensityAnalyzer()

async def server_message_handler(message : discord.Message):
    # Simplify message for ease of analysis
    cleaned_message = "".join([c for c in message.content.strip().lower() if c.isalpha() or c == ' '])

    # Use profanity-check's analysis feature to determine profanity and the chance of this message being offsensive
    profanity_chance = predict_prob([cleaned_message])[0]

    # Profanity chance threshold automatically triggers a message warning
    if profanity_chance > 0.8:
        await flag_message(message, PROFANE)
        return

    # Scan message for intent
    sentiment_scores = sentiment_analyzer.polarity_scores(cleaned_message)
    average_intent = sentiment_scores['compound']
    
    # Inverse sentiment (higher is worse)
    inv_sentiment = 1 - ((average_intent + 1) / 2)
    average_prof_inv = (profanity_chance + inv_sentiment) / 2
    print(average_prof_inv)

    if average_prof_inv > 0.6:
        await flag_message(message, AVERAGE_SENTIMENT)