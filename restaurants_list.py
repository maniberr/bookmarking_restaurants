import sqlite3
import time
import requests
import pandas as pd

DB_PATH = "restaurants.db"

def get_country_from_coords(lat, lng) -> str:
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {"lat": lat, "lon": lng, "format": "json"}
        headers = {"User-Agent": "restaurant-bookmarker/1.0"}
        response = requests.get(url, params=params, headers=headers, timeout=5)
        return response.json().get("address", {}).get("country", "Unknown")
    except Exception:
        return "Unknown"

def get_restaurants_df() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT name, address, city, rating, lat, lng, maps_url FROM restaurants", conn)
    conn.close()

    print("Looking up countries...")
    countries = []
    for _, row in df.iterrows():
        country = get_country_from_coords(row["lat"], row["lng"]) if row["lat"] and row["lng"] else "Unknown"
        print(f"  {row['name']} → {country}")
        countries.append(country)
        time.sleep(1)

    df["country"] = countries
    df = df[["country", "city", "name", "rating", "maps_url"]]
    df = df.sort_values(["country", "city", "name"]).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = get_restaurants_df()
    print(df.to_string())