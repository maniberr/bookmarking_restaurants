import os
import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_cuisine(place_id: str) -> str:
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    headers = {
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "primaryTypeDisplayName,editorialSummary"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    #print(f"  Place details response: {data}")  # debug, remove after testing

    primary_type = data.get("primaryTypeDisplayName", {}).get("text", "")
    if primary_type:
        return primary_type

    summary = data.get("editorialSummary", {}).get("text", "")
    if summary:
        return summary

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