import sqlite3
import pandas as pd

DB_PATH = "restaurants.db"

def get_restaurants_df() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT country, city,  cuisine, name, rating, maps_url FROM restaurants",
        conn
    )
    conn.close()
    df = df.sort_values(["country", "city", "cuisine","name"]).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = get_restaurants_df()
    print(df.to_string())