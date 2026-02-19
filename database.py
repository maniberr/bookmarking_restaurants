import sqlite3
import os

DB_PATH = "restaurants.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            city TEXT,
            country TEXT,
            rating REAL,
            lat REAL,
            lng REAL,
            maps_url TEXT,
            instagram_url TEXT,
            cuisine TEXT,
            date_saved TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_restaurant(name, address, city, country, rating, lat, lng, maps_url, instagram_url, cuisine):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM restaurants WHERE name = ? AND city = ?", (name, city))
    if cursor.fetchone():
        print(f"  {name} already in database, skipping.")
        conn.close()
        return
    cursor.execute("""
        INSERT INTO restaurants (name, address, city, country, rating, lat, lng, maps_url, instagram_url, cuisine)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?)
    """, (name, address, city, country, rating, lat, lng, maps_url, instagram_url, cuisine))
    conn.commit()
    conn.close()

def get_all_restaurants():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, address, city, rating, lat, lng, maps_url, instagram_url, cuisine, date_saved FROM restaurants")
    rows = cursor.fetchall()
    conn.close()
    return rows