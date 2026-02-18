import os
import sys
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

def scrape_post(url: str) -> dict:
    client = ApifyClient(os.getenv("APIFY_TOKEN"))

    run_input = {
        "directUrls": [url],
        "resultsType": "posts",
    }

    run = client.actor("apify/instagram-scraper").call(run_input=run_input)

    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    if not items:
        raise ValueError("No data returned — post may be private or URL is wrong")

    post = items[0]

    # Collect all image URLs from top-level and child posts
    urls = []
    if post.get("displayUrl"):
        urls.append(post["displayUrl"])
    for child in post.get("childPosts", []):
        if child.get("displayUrl"):
            urls.append(child["displayUrl"])

    # Collect alt texts from top-level post and all child posts
    alt_texts = []
    if post.get("alt"):
        alt_texts.append(post["alt"])
    for child in post.get("childPosts", []):
        if child.get("alt"):
            alt_texts.append(child["alt"])

    return {
        "caption": post.get("caption", ""),
        "alt_texts": alt_texts,
        "location": post.get("locationName", None),
        "image_urls": urls,
        "owner": post.get("ownerUsername", ""),
        "shortcode": post.get("shortCode", ""),
    }


if __name__ == "__main__":
    url = sys.argv[1]
    data = scrape_post(url)
    print(f"Owner: {data['owner']}")
    print(f"Location tag: {data['location']}")
    print(f"Caption preview: {data['caption'][:300]}")
    print(f"Alt Texts: {data['alt_texts']}")
    print(f"Images found: {len(data['image_urls'])}")
    print(f"Image URLs: {data['image_urls']}")