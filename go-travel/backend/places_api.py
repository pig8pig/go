"""
Enrichment Layer - Google Places API (New) for real coordinates and data
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
PLACES_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"


async def fetch_place_details(session: aiohttp.ClientSession, search_query: str) -> Optional[dict]:
    """
    Fetch a single place from Google Places API (New) Text Search.
    Returns place with coordinates and opening hours.
    """
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.currentOpeningHours,places.priceLevel,places.types,places.photos"
    }
    
    payload = {
        "textQuery": search_query,
        "maxResultCount": 1
    }
    
    try:
        async with session.post(PLACES_SEARCH_URL, headers=headers, json=payload) as response:
            data = await response.json()
            
            if not data.get("places"):
                print(f"No results for: {search_query}")
                return None
            
            place = data["places"][0]  # Get top result
            
            # Extract the data we need
            enriched = {
                "place_id": place.get("id"),
                "formatted_address": place.get("formattedAddress"),
                "lat": place.get("location", {}).get("latitude"),
                "lng": place.get("location", {}).get("longitude"),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("userRatingCount"),
                "opening_hours": place.get("currentOpeningHours", {}).get("openNow"),
                "price_level": place.get("priceLevel"),
                "types": place.get("types", []),
                "photo_reference": None
            }
            
            # Get photo reference if available
            if place.get("photos"):
                # New API uses photo resource name
                enriched["photo_reference"] = place["photos"][0].get("name")
            
            return enriched
            
    except Exception as e:
        print(f"Error fetching place '{search_query}': {e}")
        return None


async def enrich_candidates(candidates: list[dict]) -> list[dict]:
    """
    Enrich a list of candidates with Google Places data.
    Uses asyncio.gather for parallel requests (fast!).
    
    Input: List of dicts with 'name', 'search_query', 'category', 'why'
    Output: Same list enriched with lat, lng, rating, address, etc.
    """
    
    if not GOOGLE_PLACES_API_KEY:
        print("WARNING: GOOGLE_PLACES_API_KEY not set. Returning mock coordinates.")
        # Return mock data for development
        for i, candidate in enumerate(candidates):
            candidate.update({
                "place_id": f"mock_place_{i}",
                "formatted_address": f"{candidate['name']}, {candidate.get('search_query', '')}",
                "lat": 35.6762 + (i * 0.01),  # Mock coordinates
                "lng": 139.6503 + (i * 0.01),
                "rating": 4.5,
                "user_ratings_total": 1000,
                "opening_hours": True,
                "price_level": 2,
                "photo_reference": None
            })
        return candidates
    
    async with aiohttp.ClientSession() as session:
        # Create tasks for parallel fetching
        tasks = [
            fetch_place_details(session, candidate["search_query"])
            for candidate in candidates
        ]
        
        # Fetch all places in parallel
        results = await asyncio.gather(*tasks)
        
        # Merge results back into candidates
        enriched_candidates = []
        for candidate, place_data in zip(candidates, results):
            if place_data:
                # Merge original candidate data with enriched data
                enriched = {**candidate, **place_data}
                enriched_candidates.append(enriched)
            else:
                # Keep original candidate even if enrichment failed
                candidate.update({
                    "lat": None,
                    "lng": None,
                    "formatted_address": None,
                    "rating": None
                })
                enriched_candidates.append(candidate)
        
        return enriched_candidates


def get_photo_url(photo_reference: str, max_width: int = 400) -> str:
    """Generate a Google Places photo URL from a photo resource name (new API format)."""
    if not photo_reference or not GOOGLE_PLACES_API_KEY:
        return ""
    # New API format: places/{place_id}/photos/{photo_reference}/media
    return f"https://places.googleapis.com/v1/{photo_reference}/media?maxWidthPx={max_width}&key={GOOGLE_PLACES_API_KEY}"


# Sync wrapper for use in non-async contexts
def enrich_candidates_sync(candidates: list[dict]) -> list[dict]:
    """Synchronous wrapper for enrich_candidates."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop, safe to use asyncio.run()
        return asyncio.run(enrich_candidates(candidates))
    
    # Already in an event loop - use nest_asyncio or run in executor
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(asyncio.run, enrich_candidates(candidates))
        return future.result()


# For testing
if __name__ == "__main__":
    import json
    
    # Mock candidates (normally from agents.py)
    test_candidates = [
        {"name": "Tokyo Tower", "search_query": "Tokyo Tower Japan", "category": "landmark", "why": "Iconic Tokyo landmark."},
        {"name": "Senso-ji Temple", "search_query": "Senso-ji Temple Asakusa Tokyo", "category": "cultural", "why": "Ancient Buddhist temple."},
    ]
    
    enriched = enrich_candidates_sync(test_candidates)
    print(json.dumps(enriched, indent=2))
