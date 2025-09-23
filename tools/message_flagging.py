from discord import Message
import sqlite3

flagged_messages = sqlite3.connect('flagged_messages.db')
cursor_obj = flagged_messages.cursor()
table_creation_query = """
    CREATE TABLE IF NOT EXISTS FLAGGED_MESSAGES (
        Message_ID TEXT NOT NULL,
        Sender_ID TEXT NOT NULL,
        Content TEXT NOT NULL,
        Reason INT NOT NULL,
        PRIMARY KEY (Message_ID)
    );
"""

cursor_obj.execute(table_creation_query)

async def flag_message(message : Message, flag : int):
    cursor_obj.execute(f"INSERT INTO FLAGGED_MESSAGES (Message_ID, Sender_ID, Content, Reason) \
                        VALUES ('{message.id}', '{message.author.id}', '{message.content}', {flag})")