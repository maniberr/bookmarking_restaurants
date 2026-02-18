import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_with_groq(caption: str, descriptions: list = []) -> str:
    combined = caption + " " + " ".join(descriptions)
    combined = combined.strip()

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": f"""This is text from an Instagram post about one or more restaurants or cafes.
Extract all restaurant or cafe names and the city or cities they are in.
Reply in this exact format, one per line:
RESTAURANT: <name> | CITY: <city>
If you cannot find a city for a restaurant, write CITY: UNKNOWN.
If you cannot find any restaurants, reply with NOT_FOUND.
Text: {combined}"""
            }
        ]
    )
    return response.choices[0].message.content.strip()

def describe_image_with_groq(image_url: str) -> str:
    response = groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    },
                    {
                        "type": "text",
                        "text": "Does this image show a restaurant or cafe? If yes, what is its name and what city is it in? Reply only with the name and city, nothing else. If you cannot tell, reply NOT_FOUND."
                    }
                ]
            }
        ]
    )
    return response.choices[0].message.content.strip()

def parse_results(raw: str) -> list:
    results = []
    for line in raw.strip().split("\n"):
        if "RESTAURANT:" in line and "CITY:" in line:
            parts = line.split("|")
            name = parts[0].replace("RESTAURANT:", "").strip()
            city = parts[1].replace("CITY:", "").strip()
            results.append({"restaurant": name, "city": city})
    return results

def extract_restaurants(caption: str, image_urls: list = []) -> list:
    if not caption and not image_urls:
        return []

    # Get vision descriptions for all images
    image_descriptions = []
    for url in image_urls:
        description = describe_image_with_groq(url)
        if description != "NOT_FOUND":
            image_descriptions.append(description)

    # Combine caption and image descriptions into one extraction call
    raw = extract_with_groq(caption, image_descriptions)

    if raw == "NOT_FOUND":
        return []

    results = parse_results(raw)

    # Deduplicate by restaurant name
    seen = set()
    unique = []
    for r in results:
        if r["restaurant"] not in seen:
            seen.add(r["restaurant"])
            unique.append(r)

    return unique


if __name__ == "__main__":
    caption = "NYC date spots that quietly win second dates…Find them on Cerca."
    image_urls = ['https://scontent-atl3-3.cdninstagram.com/v/t51.2885-15/625099063_17909440698319700_2374618532714062190_n.jpg?stp=dst-jpg_e15_fr_p1080x1080_tt6&_nc_ht=scontent-atl3-3.cdninstagram.com&_nc_cat=108&_nc_oc=Q6cZ2QEuX7y5K6JtKiskf3e52jmQolcH-ZPmfxBYV1iYQvL7vp3wOKDxEt5kQafXrQ5zUEs&_nc_ohc=G8DRU-B8boUQ7kNvwEze8lR&_nc_gid=7wPQo4KN5hc_7Es_ttUN3Q&edm=APs17CUBAAAA&ccb=7-5&oh=00_AfvDbJ8d7lGPN2-8LzhMUe3c-70DHa6J4Khmrjl42Ni4ow&oe=699BE517&_nc_sid=10d13b', 'https://scontent-atl3-3.cdninstagram.com/v/t51.2885-15/625099063_17909440698319700_2374618532714062190_n.jpg?stp=dst-jpg_e15_fr_p1080x1080_tt6&_nc_ht=scontent-atl3-3.cdninstagram.com&_nc_cat=108&_nc_oc=Q6cZ2QEuX7y5K6JtKiskf3e52jmQolcH-ZPmfxBYV1iYQvL7vp3wOKDxEt5kQafXrQ5zUEs&_nc_ohc=G8DRU-B8boUQ7kNvwEze8lR&_nc_gid=7wPQo4KN5hc_7Es_ttUN3Q&edm=APs17CUBAAAA&ccb=7-5&oh=00_AfvDbJ8d7lGPN2-8LzhMUe3c-70DHa6J4Khmrjl42Ni4ow&oe=699BE517&_nc_sid=10d13b', 'https://scontent-atl3-3.cdninstagram.com/v/t51.2885-15/625960507_17909440695319700_4205767478453858649_n.jpg?stp=dst-jpg_e15_fr_p1080x1080_tt6&_nc_ht=scontent-atl3-3.cdninstagram.com&_nc_cat=108&_nc_oc=Q6cZ2QEuX7y5K6JtKiskf3e52jmQolcH-ZPmfxBYV1iYQvL7vp3wOKDxEt5kQafXrQ5zUEs&_nc_ohc=fqsl1grW-RIQ7kNvwHbLOxK&_nc_gid=7wPQo4KN5hc_7Es_ttUN3Q&edm=APs17CUBAAAA&ccb=7-5&oh=00_AfvXx0JuJF9QoRr-v8CdgYSt93uIcN0IZ9UKGJhF-LuDuQ&oe=699BFD17&_nc_sid=10d13b', 'https://scontent-atl3-3.cdninstagram.com/v/t51.2885-15/625984853_17909440713319700_1241828334812504264_n.jpg?stp=dst-jpg_e15_fr_p1080x1080_tt6&_nc_ht=scontent-atl3-3.cdninstagram.com&_nc_cat=108&_nc_oc=Q6cZ2QEuX7y5K6JtKiskf3e52jmQolcH-ZPmfxBYV1iYQvL7vp3wOKDxEt5kQafXrQ5zUEs&_nc_ohc=fpMaRIZG7e4Q7kNvwGiOFaB&_nc_gid=7wPQo4KN5hc_7Es_ttUN3Q&edm=APs17CUBAAAA&ccb=7-5&oh=00_Afv91o8sqmTGIbH1iw1fnBZnAzByhc509aFzJRT54DhTqg&oe=699C0462&_nc_sid=10d13b', 'https://scontent-atl3-3.cdninstagram.com/v/t51.2885-15/626409271_17909440716319700_2286205812265645376_n.jpg?stp=dst-jpg_e15_fr_p1080x1080_tt6&_nc_ht=scontent-atl3-3.cdninstagram.com&_nc_cat=108&_nc_oc=Q6cZ2QEuX7y5K6JtKiskf3e52jmQolcH-ZPmfxBYV1iYQvL7vp3wOKDxEt5kQafXrQ5zUEs&_nc_ohc=GK7qRvUZpZ4Q7kNvwFx071L&_nc_gid=7wPQo4KN5hc_7Es_ttUN3Q&edm=APs17CUBAAAA&ccb=7-5&oh=00_Afu-MLg1B5wgqgPyUzq1V8zHB5QW8xXFArKJSezLIw-YjA&oe=699BF9FC&_nc_sid=10d13b']
    results = extract_restaurants(caption, image_urls=image_urls)
    for r in results:
        print(f"Restaurant: {r['restaurant']} | City: {r['city']}")