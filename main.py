import sys
from scraper import scrape_post
from extractor import extract_restaurants
from maps import find_place
from database import init_db, save_restaurant
from visualizer import generate_map
from geocoding_country import get_country
import time
    
def process_url(url: str):
    print(f"\nProcessing: {url}")

    print("Scraping post...")
    post_data = scrape_post(url)

    print("Extracting restaurants...")
    restaurants = extract_restaurants(post_data["caption"], post_data["image_urls"], post_data["owner"])

    if not restaurants:
        print("No restaurants found.")
        return

    print(f"Found {len(restaurants)} restaurant(s):")
    for r in restaurants:
        place = find_place(r["restaurant"], r["city"])
        if place:
            print(f"  Looking up country for {place['name']}...")
            country = get_country(place["lat"], place["lng"])
            time.sleep(1)
            print(f"  + {place['name']} — {place['address']} — {country}")
            save_restaurant(
                name=place["name"],
                address=place["address"],
                city=r["city"],
                country=country,
                rating=place["rating"],
                lat=place["lat"],
                lng=place["lng"],
                maps_url=place["maps_url"],
                instagram_url=url
            )
        else:
            print(f"  Could not find {r['restaurant']} on Google Maps.")

def main(urls: list):
    init_db()

    for url in urls:
        process_url(url)

    print("\nGenerating map...")
    generate_map()
    print("Done! Open map.html in your browser.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <url1> <url2> <url3> ...")
        sys.exit(1)
    main(sys.argv[1])