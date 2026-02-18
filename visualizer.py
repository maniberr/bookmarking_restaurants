import folium
from folium.plugins import MarkerCluster
from database import get_all_restaurants

def generate_map(output_path="map.html"):
    restaurants = get_all_restaurants()

    if not restaurants:
        print("No restaurants in database yet.")
        return

    avg_lat = sum(r[4] for r in restaurants) / len(restaurants)
    avg_lng = sum(r[5] for r in restaurants) / len(restaurants)

    m = folium.Map(
        location=[avg_lat, avg_lng],
        zoom_start=13,
        tiles=None
    )

    # Dark elegant tile layer
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr="CartoDB",
        name="Dark Matter",
        max_zoom=19
    ).add_to(m)

    for r in restaurants:
        name, address, city, rating, lat, lng, maps_url, instagram_url, date_saved = r
        if lat and lng:
            stars = "★" * int(rating) + "☆" * (5 - int(rating)) if rating else "N/A"
            popup_html = f"""
                <div style="
                    font-family: 'Georgia', serif;
                    background: #1a1a1a;
                    color: #f0ead6;
                    padding: 16px;
                    border-radius: 4px;
                    min-width: 220px;
                    border-left: 3px solid #c9a96e;
                ">
                    <div style="font-size: 15px; font-weight: bold; color: #c9a96e; margin-bottom: 6px;">
                        {name}
                    </div>
                    <div style="font-size: 11px; color: #888; margin-bottom: 8px; line-height: 1.4;">
                        {address or city}
                    </div>
                    <div style="font-size: 13px; color: #c9a96e; margin-bottom: 10px;">
                        {stars}
                    </div>
                    <div style="display: flex; gap: 10px; font-size: 11px;">
                        <a href="{maps_url}" target="_blank" style="
                            color: #1a1a1a;
                            background: #c9a96e;
                            padding: 4px 10px;
                            border-radius: 2px;
                            text-decoration: none;
                            font-family: sans-serif;
                        ">Maps</a>
                        <a href="{instagram_url}" target="_blank" style="
                            color: #c9a96e;
                            border: 1px solid #c9a96e;
                            padding: 4px 10px;
                            border-radius: 2px;
                            text-decoration: none;
                            font-family: sans-serif;
                        ">Instagram</a>
                    </div>
                </div>
            """

            icon_html = """
                <div style="
                    width: 14px;
                    height: 14px;
                    background: #c9a96e;
                    border-radius: 50%;
                    border: 2px solid #f0ead6;
                    box-shadow: 0 0 8px rgba(201, 169, 110, 0.8);
                "></div>
            """

            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(
                    folium.IFrame(popup_html, width=260, height=160),
                    max_width=260
                ),
                tooltip=folium.Tooltip(
                    f"<span style='font-family:Georgia;color:#c9a96e;background:#1a1a1a;padding:4px 8px;border-radius:2px;'>{name}</span>",
                    permanent=False
                ),
                icon=folium.DivIcon(html=icon_html, icon_size=(14, 14), icon_anchor=(7, 7))
            ).add_to(m)

    # Inject custom CSS into the map HTML
    custom_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=EB+Garamond&display=swap');

        body {
            margin: 0;
            background: #0f0f0f;
        }

        .leaflet-container {
            background: #0f0f0f;
            font-family: 'EB Garamond', serif;
        }

        .leaflet-popup-content-wrapper {
            background: transparent !important;
            box-shadow: none !important;
            padding: 0 !important;
            border-radius: 4px !important;
        }

        .leaflet-popup-tip {
            background: #1a1a1a !important;
        }

        .leaflet-popup-content {
            margin: 0 !important;
        }

        #title-overlay {
            position: fixed;
            top: 24px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            background: rgba(15, 15, 15, 0.85);
            backdrop-filter: blur(8px);
            padding: 12px 28px;
            border: 1px solid #c9a96e;
            border-radius: 2px;
            text-align: center;
            pointer-events: none;
        }

        #title-overlay h1 {
            font-family: 'Playfair Display', serif;
            color: #c9a96e;
            font-size: 18px;
            font-weight: 600;
            margin: 0;
            letter-spacing: 0.15em;
            text-transform: uppercase;
        }

        #title-overlay p {
            font-family: 'EB Garamond', serif;
            color: #888;
            font-size: 12px;
            margin: 4px 0 0 0;
            letter-spacing: 0.05em;
        }

        #count-overlay {
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 1000;
            background: rgba(15, 15, 15, 0.85);
            backdrop-filter: blur(8px);
            padding: 10px 18px;
            border: 1px solid #333;
            border-radius: 2px;
            pointer-events: none;
        }

        #count-overlay span {
            font-family: 'Playfair Display', serif;
            color: #c9a96e;
            font-size: 22px;
            font-weight: 600;
        }

        #count-overlay p {
            font-family: 'EB Garamond', serif;
            color: #666;
            font-size: 11px;
            margin: 2px 0 0 0;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
    </style>

    <div id="title-overlay">
        <h1>My Restaurant List</h1>
        <p>Saved from Instagram</p>
    </div>

    <div id="count-overlay">
        <span>{count}</span>
        <p>Places Saved</p>
    </div>
    """.replace("{count}", str(len(restaurants)))

    m.get_root().html.add_child(folium.Element(custom_css))
    m.save(output_path)
    print(f"Map saved to {output_path} — open it in your browser!")


if __name__ == "__main__":
    generate_map()