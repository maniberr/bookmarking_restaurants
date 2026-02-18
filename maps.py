import os
import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def find_place(restaurant: str, city: str) -> dict:
    query = f"{restaurant} {city}"

    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": query,
        "inputtype": "textquery",
        "fields": "name,formatted_address,geometry,rating,place_id",
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()
  
    if not data.get("candidates"):
        return None

    place = data["candidates"][0]
    return {
        "name": place.get("name"),
        "address": place.get("formatted_address"),
        "rating": place.get("rating"),
        "lat": place["geometry"]["location"]["lat"],
        "lng": place["geometry"]["location"]["lng"],
        "maps_url": f"https://www.google.com/maps/place/?q=place_id:{place.get('place_id')}"
    }