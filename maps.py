import os
import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

CUISINE_TYPES = {
    "american_restaurant", "bakery", "bar", "barbecue_restaurant",
    "brazilian_restaurant", "breakfast_restaurant", "brunch_restaurant",
    "cafe", "chinese_restaurant", "coffee_shop", "fast_food_restaurant",
    "french_restaurant", "greek_restaurant", "hamburger_restaurant",
    "ice_cream_shop", "indian_restaurant", "indonesian_restaurant",
    "italian_restaurant", "japanese_restaurant", "korean_restaurant",
    "lebanese_restaurant", "mediterranean_restaurant", "mexican_restaurant",
    "middle_eastern_restaurant", "pizza_restaurant", "ramen_restaurant",
    "sandwich_shop", "seafood_restaurant", "spanish_restaurant",
    "steak_house", "sushi_restaurant", "thai_restaurant",
    "turkish_restaurant", "vegan_restaurant", "vegetarian_restaurant",
    "vietnamese_restaurant"
}

def get_cuisine(place_id: str) -> str:
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "types",
        "key": GOOGLE_API_KEY
    }
    response = requests.get(url, params=params)
    types = response.json().get("result", {}).get("types", [])
    for t in types:
        if t in CUISINE_TYPES:
            return t.replace("_restaurant", "").replace("_", " ").title()
    return "Restaurant"

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

    if place.get("business_status") == "PERMANENTLY_CLOSED":
        print(f"  ⚠️ {place.get('name')} is permanently closed, skipping.")
        return None
    
    place_id = place.get("place_id")
    cuisine = get_cuisine(place_id) if place_id else "Restaurant"
    return {
        "name": place.get("name"),
        "address": place.get("formatted_address"),
        "rating": place.get("rating"),
        "lat": place["geometry"]["location"]["lat"],
        "lng": place["geometry"]["location"]["lng"],
        "maps_url": f"https://www.google.com/maps/place/?q=place_id:{place.get('place_id')}",
        "cuisine": cuisine
    }