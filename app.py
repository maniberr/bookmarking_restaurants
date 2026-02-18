import streamlit as st
from scraper import scrape_post
from extractor import extract_restaurants
from maps import find_place
from database import init_db, save_restaurant, get_all_restaurants
from visualizer import generate_map
from restaurants_list import get_restaurants_df
import streamlit.components.v1 as components
import pandas as pd

st.set_page_config(
    page_title="Restaurant Bookmarker",
    page_icon="🍽️",
    layout="wide"
)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=EB+Garamond&display=swap');

        html, body, [class*="css"] {
            font-family: 'EB Garamond', serif;
        }

        .main {
            background-color: #0f0f0f;
            color: #f0ead6;
        }

        h1, h2, h3 {
            font-family: 'Playfair Display', serif !important;
            color: #c9a96e !important;
        }

        .stTextArea textarea {
            background-color: #1a1a1a !important;
            color: #f0ead6 !important;
            border: 1px solid #333 !important;
            font-family: 'EB Garamond', serif !important;
            font-size: 15px !important;
        }

        .stButton > button {
            background-color: #c9a96e !important;
            color: #0f0f0f !important;
            font-family: 'Playfair Display', serif !important;
            font-size: 15px !important;
            border: none !important;
            padding: 10px 28px !important;
            border-radius: 2px !important;
            letter-spacing: 0.08em !important;
        }

        .stButton > button:hover {
            background-color: #b8935a !important;
        }

        .restaurant-card {
            background: #1a1a1a;
            border-left: 3px solid #c9a96e;
            padding: 14px 18px;
            margin-bottom: 12px;
            border-radius: 2px;
        }

        .restaurant-name {
            font-family: 'Playfair Display', serif;
            color: #c9a96e;
            font-size: 17px;
            font-weight: 600;
        }

        .restaurant-detail {
            color: #888;
            font-size: 13px;
            margin-top: 4px;
        }

        .stars {
            color: #c9a96e;
            font-size: 14px;
            margin-top: 4px;
        }
    </style>
""", unsafe_allow_html=True)

init_db()

st.title("Restaurant Bookmarker")
st.markdown("<p style='color:#888;font-family:EB Garamond,serif;font-size:16px;'>Paste Instagram post URLs to extract and save restaurants to your map.</p>", unsafe_allow_html=True)

st.markdown("---")

# URL input
urls_input = st.text_area(
    "Instagram URLs (one per line)",
    placeholder="https://www.instagram.com/p/ABC123/\nhttps://www.instagram.com/p/XYZ456/",
    height=120
)

run = st.button("Extract & Save Restaurants")

if run and urls_input.strip():
    urls = [u.strip() for u in urls_input.strip().split("\n") if u.strip()]
    all_found = []

    for url in urls:
        with st.spinner(f"Processing {url}..."):
            try:
                post_data = scrape_post(url)
                restaurants = extract_restaurants(
                    post_data["caption"],
                    post_data["image_urls"],
                    post_data["owner"]
                )

                if not restaurants:
                    st.warning(f"No restaurants found in: {url}")
                    continue

                for r in restaurants:
                    place = find_place(r["restaurant"], r["city"])
                    if place:
                        save_restaurant(
                            name=place["name"],
                            address=place["address"],
                            city=r["city"],
                            rating=place["rating"],
                            lat=place["lat"],
                            lng=place["lng"],
                            maps_url=place["maps_url"],
                            instagram_url=url
                        )
                        all_found.append(place)
                    else:
                        st.warning(f"Could not find '{r['restaurant']}' on Google Maps.")

            except Exception as e:
                st.error(f"Error processing {url}: {e}")

    if all_found:
        st.success(f"Saved {len(all_found)} restaurant(s)!")
        for place in all_found:
            stars = "★" * int(place["rating"]) + "☆" * (5 - int(place["rating"])) if place.get("rating") else ""
            st.markdown(f"""
                <div class="restaurant-card">
                    <div class="restaurant-name">{place['name']}</div>
                    <div class="restaurant-detail">{place['address']}</div>
                    <div class="stars">{stars}</div>
                    <div style="margin-top:8px;">
                        <a href="{place['maps_url']}" target="_blank" style="color:#c9a96e;font-size:13px;">View on Google Maps →</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# Map section
st.markdown("<h2>Your Restaurant Map</h2>", unsafe_allow_html=True)

all_restaurants = get_all_restaurants()
if all_restaurants:
    generate_map("map.html")
    with open("map.html", "r") as f:
        map_html = f.read()
    components.html(map_html, height=600, scrolling=False)
else:
    st.markdown("<p style='color:#555;'>No restaurants saved yet. Paste some URLs above to get started.</p>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<h2>All Saved Restaurants</h2>", unsafe_allow_html=True)

if get_all_restaurants():
    with st.spinner("Loading restaurant list..."):
        df = get_restaurants_df()
        df.columns = ["Country", "City", "Restaurant Name", "Rating", "Google Maps URL"]
        df["Rating"] = df["Rating"].apply(lambda x: "★" * int(x) + "☆" * (5 - int(x)) if pd.notna(x) and x else "N/A")
        df["Google Maps URL"] = df["Google Maps URL"].apply(lambda x: f'<a href="{x}" target="_blank">View →</a>' if x else "")
        st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
else:
    st.markdown("<p style='color:#555;'>No restaurants saved yet.</p>", unsafe_allow_html=True)