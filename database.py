import sqlite3
import time

DB_NAME = "titanflow_data.db"

def init_db():
    """Creates the warehouse if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # We create a table to store product data and a timestamp (to know how old data is)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            keyword TEXT PRIMARY KEY,
            product_name TEXT,
            price TEXT,
            timestamp REAL
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Warehouse (Database) Initialized.")

def save_product(keyword, name, price):
    """Stores data in the warehouse."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # specific 'REPLACE' command updates the data if we already have this keyword
    cursor.execute("REPLACE INTO products (keyword, product_name, price, timestamp) VALUES (?, ?, ?, ?)",
                   (keyword, name, price, time.time()))
    conn.commit()
    conn.close()

def get_cached_product(keyword):
    """Checks the warehouse for data."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT product_name, price, timestamp FROM products WHERE keyword=?", (keyword,))
    data = cursor.fetchone()
    conn.close()
    
    if data:
        # Check if data is older than 24 hours (86400 seconds)
        # If it's too old, we return None so the scraper runs again.
        if time.time() - data[2] > 86400: 
            return None 
        return {"product": data[0], "price": data[1], "source": "Cache (Fast)"}
    return None

# Run initialization once
if __name__ == "__main__":
    init_db()
