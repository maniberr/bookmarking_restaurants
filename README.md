# Instagram Post Bookmarking
Moving to a new city, visiting a new place, seeing myriads of Instagram posts of places you'd like to try but don't have the patience to research and save all? Pass me the instagram post and I'll bookmark all places to a custom map!

# Overview

A Python tool that takes Instagram post URLs, extracts restaurant names and locations using AI, finds them on Google Maps, and saves them to an interactive map that the user can explore in their browser.

# How It Works

1. **Scrape** — fetches the Instagram post via Apify (no Instagram login required)
2. **Extract** — uses Groq (Llama 3) to identify restaurant names and cities from the caption and images
3. **Geocode** — looks up each restaurant on Google Maps to get coordinates, address, and rating
4. **Save** — stores results in a local SQLite database and generates a beautiful interactive map

# Demo

![map screenshot](assets/map_screenshot.png)

# Usage

Pass one or more Instagram post URLs:
```bash
python main.py "https://www.instagram.com/p/ABC123/" "https://www.instagram.com/p/XYZ456/"
```

When finished, open `map.html` in your browser to see all your saved restaurants as interactive pins on a dark map.

# Project Structure
```
├── main.py          # entry point, orchestrates the full pipeline
├── scraper.py       # fetches Instagram post data via Apify
├── extractor.py     # extracts restaurant names and cities using Groq AI
├── maps.py          # looks up places via Google Places API
├── database.py      # saves results to SQLite
├── visualizer.py    # generates the interactive HTML map
├── requirements.txt
└── .env             # API keys (never committed)
```

# Limitations

- Only works on public Instagram posts
- Restaurant detection depends on the post having visible text or a descriptive caption
- Google Places API requires billing to be enabled (but has a free tier)

# Future Improvements

- [ ] Web UI to paste URLs without using the terminal
- [ ] Filter map by city or cuisine type
- [ ] Support for TikTok and other platforms