import sys
from scraper import scrape_post
from extractor import extract_restaurants
from maps import find_place

def main(url: str):
    print("Scraping post...")
    post_data = scrape_post(url)

    print("Extracting restaurants...")
    restaurants = extract_restaurants(post_data["caption"], post_data["image_urls"], post_data["owner"])
    print(restaurants)
    if not restaurants:
        print("No restaurants found.")
        return

    print(f"\nFound {len(restaurants)} restaurant(s):\n")
    for r in restaurants:
        place = find_place(r["restaurant"], r["city"])
        if place:
            print(f"Name: {place['name']}")
            print(f"Address: {place['address']}")
            print(f"Rating: {place['rating']}")
            print(f"Coordinates: {place['lat']}, {place['lng']}")
            print(f"Maps URL: {place['maps_url']}")
            print()
        else:
            print(f"Could not find {r['restaurant']} on Google Maps.\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <instagram_url>")
        sys.exit(1)
    main(sys.argv[1])