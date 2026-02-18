import time
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="restaurant-bookmarker/1.0")

def get_country(lat, lng) -> str:
    try:
        location = geolocator.reverse(f"{lat}, {lng}", language="en")
        time.sleep(1)
        return location.raw.get("address", {}).get("country", "Unknown")
    except Exception:
        return "Unknown"