from discord import Embed
import sqlite3

config = sqlite3.connect("modchannels.db")

cursor_obj = config.cursor()
table_creation_query = """
    CREATE TABLE IF NOT EXISTS MODCHANNELS (
        server_id TEXT PRIMARY KEY,
        channel_id TEXT
    );
"""

cursor_obj.execute(table_creation_query)
config.commit()


async def get_moderation_channel(server_id : str):
    cursor_obj.execute("SELECT channel_id FROM MODCHANNELS WHERE server_id =", server_id)
    return str(cursor_obj.fetchone())

async def set_moderation_channel(server_id : str, channel_id : str):
    cursor_obj.execute(f"INSERT OR REPLACE INTO MODCHANNELS (server_id, channel_id) VALUES ('{server_id}', '{channel_id}')")
    config.commit()

async def send_moderation_embed(channel, embed : Embed):
    await channel.send(embed=embed)