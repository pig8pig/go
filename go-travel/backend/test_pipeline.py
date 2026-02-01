"""
Full pipeline integration test - simulates what main.py does
"""
import sys
sys.path.insert(0, '.')

from agents import generate_candidates
from places_api import enrich_candidates_sync, get_photo_url
from scoring import rank_places
from weather import fetch_weather_sync
from solver import solve_itinerary
from response_models import format_itinerary_response, format_error_response
import json

def test_full_pipeline():
    # Inputs (simulating frontend request)
    city = "Vancouver"
    vibe = "nature lover"
    start_date = "2026-02-15"
    end_date = "2026-02-17"
    num_days = 3
    num_places = 12
    
    print("="*60)
    print(f"FULL PIPELINE TEST: {city}, {num_days} days, '{vibe}'")
    print("="*60)
    
    # Step 1: Generate candidates
    print("\n[1] Generating candidates with Claude...")
    candidates = generate_candidates(city, vibe, num_places)
    if not candidates:
        print("ERROR: No candidates generated")
        return
    print(f"    Generated {len(candidates)} candidates")
    for c in candidates[:3]:
        print(f"    - {c['name']}")
    
    # Step 2: Enrich with Google Places
    print("\n[2] Enriching with Google Places...")
    enriched = enrich_candidates_sync(candidates)
    for p in enriched:
        if p.get("photo_reference"):
            p["photo_url"] = get_photo_url(p["photo_reference"])
    valid = [p for p in enriched if p.get("lat")]
    print(f"    Enriched {len(valid)}/{len(candidates)} with coordinates")
    
    # Step 3: Fetch weather
    print("\n[3] Fetching weather...")
    weather = fetch_weather_sync(city)
    if weather:
        print(f"    Weather: {weather.get('temp')}°C, {weather.get('description')}")
    else:
        print("    Weather: unavailable")
    
    # Step 4: Score places
    print("\n[4] Scoring places...")
    scored = rank_places(enriched, weather=weather)
    print(f"    {len(scored)} places passed threshold")
    for p in scored[:3]:
        print(f"    - {p['name']}: {p.get('score', 0):.1f}")
    
    # Step 5: Solve itinerary
    print("\n[5] Solving multi-day itinerary...")
    coords = [(p["lat"], p["lng"]) for p in scored if p.get("lat")]
    if coords:
        hotel = (sum(c[0] for c in coords)/len(coords), sum(c[1] for c in coords)/len(coords))
    else:
        hotel = None
    
    solver_output = solve_itinerary(scored, hotel, num_days, time_limit_seconds=10)
    total = sum(d["num_places"] for d in solver_output)
    print(f"    Assigned {total} places across {num_days} days")
    
    # Step 6: Format response
    print("\n[6] Formatting response...")
    response = format_itinerary_response(
        city=city,
        vibe=vibe,
        num_days=num_days,
        start_date=start_date,
        solver_output=solver_output,
        original_places=scored,
        hotel_coords=hotel,
    )
    
    # Print summary
    print("\n" + "="*60)
    print("FINAL RESPONSE (what frontend receives)")
    print("="*60)
    print(f"Success: {response['success']}")
    print(f"City: {response['trip']['city']}")
    print(f"Dates: {response['trip']['start_date']} to {response['trip']['end_date']}")
    print(f"Total places: {response['trip']['total_places']}")
    print(f"Dropped: {response['trip']['places_dropped']}")
    
    for day in response['days']:
        if day['places']:
            print(f"\nDay {day['day_number']} ({day['date']}):")
            for p in day['places'][:4]:
                print(f"  {p['time']['arrival']} - {p['name']}")
            if len(day['places']) > 4:
                print(f"  ... and {len(day['places'])-4} more")
    
    print("\n[✓] Pipeline complete!")
    return response

if __name__ == "__main__":
    test_full_pipeline()
