import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_with_groq(caption: str, descriptions: list = [], account_name: str = "") -> str:
    combined = caption + " " + " ".join(descriptions)
    combined = combined.strip()

    exclusion = f"The Instagram account name is '{account_name}' — do not include this as a restaurant." if account_name else ""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": f"""This is text from an Instagram post about one or more restaurants or cafes.
Extract all restaurant or cafe names and the city or cities they are in.
{exclusion}
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
                        "text": """Look at this image carefully.
Read any and all text visible in the image — signs, posters, menus, walls, windows, receipts, anything.
If any of that text appears to be the name of a restaurant, bar, or cafe, extract it.
Also extract any neighborhood, street, or city mentioned.
Reply in this exact format: NAME: <name> | LOCATION: <location>
If no location is visible, write LOCATION: UNKNOWN.
Only reply NOT_FOUND if you are certain there is absolutely no restaurant or bar name anywhere in the image."""
                        }
                ]
            }
        ]
    )
    #print(f"Image description: {response.choices[0].message.content.strip()}\n")
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

def extract_restaurants(caption: str, image_urls: list = [], account_name: str = "") -> list:
    if not caption and not image_urls:
        return []

    # Get vision descriptions for all images
    image_descriptions = []
    for url in image_urls:
        description = describe_image_with_groq(url)
        if description != "NOT_FOUND":
            image_descriptions.append(description)

    # Combine caption and image descriptions into one extraction call
    raw = extract_with_groq(caption, image_descriptions, account_name)

    if raw == "NOT_FOUND":
        return []

    results = parse_results(raw)

    # For any result with UNKNOWN city, try to infer from caption
    unknown = [r for r in results if r["city"] == "UNKNOWN"]
    if unknown:
        city_response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": f"""Based on this Instagram caption, what city or cities are being referred to?
Reply with only the city name(s), comma separated. If you cannot tell, reply UNKNOWN.
Caption: {caption}"""
                }
            ]
        )
        inferred_city = city_response.choices[0].message.content.strip()

        if inferred_city != "UNKNOWN":
            for r in results:
                if r["city"] == "UNKNOWN":
                    r["city"] = inferred_city

    # Deduplicate by restaurant name
    seen = set()
    unique = []
    for r in results:
        if r["restaurant"] not in seen:
            seen.add(r["restaurant"])
            unique.append(r)

    return unique