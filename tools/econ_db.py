# tools/econ_db.py

import sqlite3

config = sqlite3.connect("database.db")

# This assumes a starting cash value of 100 (TODO: add this to environment setup)
cursor_obj = config.cursor()
table_creation_query = """
    CREATE TABLE IF NOT EXISTS ECONOMY (
        server_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        cash INTEGER DEFAULT 100,
        bank INTEGER DEFAULT 0,
        PRIMARY KEY (server_id, user_id)
    );
"""

cursor_obj.execute(table_creation_query)
config.commit()

def update_cash(server_id, user_id, amount):
    initial_insert_query = """
        INSERT OR IGNORE INTO ECONOMY (server_id, user_id) 
        VALUES (?, ?);
    """
    cursor_obj.execute(initial_insert_query, (server_id, user_id))
    
    update_query = """
        UPDATE ECONOMY
        SET cash = cash + ?
        WHERE server_id = ? AND user_id = ?;
    """
    cursor_obj.execute(update_query, (amount, server_id, user_id))
    config.commit()

def update_bank(server_id, user_id, amount):
    initial_insert_query = """
        INSERT OR IGNORE INTO ECONOMY (server_id, user_id) 
        VALUES (?, ?);
    """
    cursor_obj.execute(initial_insert_query, (server_id, user_id))
    
    update_query = """
        UPDATE ECONOMY
        SET bank = bank + ?
        WHERE server_id = ? AND user_id = ?;
    """
    cursor_obj.execute(update_query, (amount, server_id, user_id))
    config.commit()

def get_balance(server_id, user_id):
    query = """
        SELECT cash, bank
        FROM ECONOMY
        WHERE server_id = ? AND user_id = ?;
    """
    cursor_obj.execute(query, (server_id, user_id))
    
    # Fetch one row (since the server_id/user_id combo is unique)
    result = cursor_obj.fetchone() 
    
    if result:
        return {"cash": result[0], "bank": result[1]}
    else:
        return {"cash": 0, "bank": 0} 
    
