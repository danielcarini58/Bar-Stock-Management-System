import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

print("DB PATH:", DB_PATH)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()



cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
    role TEXT NOT NULL           
)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    stock INTEGER NOT NULL,
    Status TEXT NOT NULL,
    LastRestock TEXT NOT NULL
)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    sale_date TEXT NOT NULL,
    cost REAL NOT NULL,
    FOREIGN KEY (item_id) REFERENCES items(id)
)""")
               
cursor.execute("""
CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    supplier TEXT NOT NULL,
    description TEXT NOT NULL,           
    purchase_date TEXT NOT NULL,
    status TEXT NOT NULL
)""")                          

cursor.execute("""
CREATE TABLE IF NOT EXISTS purchase_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (purchase_id) REFERENCES purchases(id),
    FOREIGN KEY (item_id) REFERENCES items(id)
)""")                              

cursor.execute("""
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL,
    start_date TEXT NOT NULL,                      
    end_date TEXT NOT NULL,
    details TEXT NOT NULL,
    generated_at TEXT NOT NULL
)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS waste(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    waste_date TEXT NOT NULL,
    cost REAL NOT NULL,      
    reason TEXT NOT NULL,                
    FOREIGN KEY (item_id) REFERENCES items(id)
)""")
                                                  
conn.commit()
conn.close()

print("Database created")
