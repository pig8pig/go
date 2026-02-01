"""
Test the full response format with solver output
"""
from solver import solve_itinerary
from response_models import format_itinerary_response, format_error_response
import json

# Simulate what main.py would do
def test_full_pipeline():
    print("="*60)
    print("FULL PIPELINE TEST: Tokyo 3-Day Trip")
    print("="*60)
    
    # Input parameters (from frontend)
    city = "Tokyo"
    vibe = "adventure"
    start_date = "2026-02-15"
    num_days = 3
    
    # Simulated scored places (normally from agents + places_api + scoring)
    scored_places = [
        {"place_id": "t1", "name": "Senso-ji Temple", "lat": 35.7148, "lng": 139.7967, "score": 95, "category": "landmark", "why": "Tokyo's oldest temple with stunning architecture", "rating": 4.6, "review_count": 52341, "formatted_address": "2-3-1 Asakusa, Taito City"},
        {"place_id": "t2", "name": "Tokyo Skytree", "lat": 35.7101, "lng": 139.8107, "score": 88, "category": "landmark", "why": "Breathtaking views from Japan's tallest tower", "rating": 4.5, "review_count": 41234},
        {"place_id": "t3", "name": "Shibuya Crossing", "lat": 35.6595, "lng": 139.7004, "score": 82, "category": "landmark", "why": "World's busiest pedestrian crossing", "rating": 4.4, "review_count": 28123},
        {"place_id": "t4", "name": "Meiji Shrine", "lat": 35.6764, "lng": 139.6993, "score": 90, "category": "cultural", "why": "Serene Shinto shrine in a forested setting", "rating": 4.7, "review_count": 35678},
        {"place_id": "t5", "name": "teamLab Borderless", "lat": 35.6264, "lng": 139.7841, "score": 92, "category": "museum", "why": "Immersive digital art experience", "rating": 4.8, "review_count": 15234},
        {"place_id": "t6", "name": "Tsukiji Outer Market", "lat": 35.6654, "lng": 139.7707, "score": 85, "category": "shopping", "why": "Fresh sushi and local street food", "rating": 4.3, "review_count": 22456},
        {"place_id": "t7", "name": "Shinjuku Gyoen", "lat": 35.6852, "lng": 139.7100, "score": 78, "category": "nature", "why": "Beautiful gardens perfect for relaxation", "rating": 4.6, "review_count": 18234},
        {"place_id": "t8", "name": "Akihabara", "lat": 35.7023, "lng": 139.7745, "score": 75, "category": "shopping", "why": "Electric town for anime and tech lovers", "rating": 4.2, "review_count": 12345},
        {"place_id": "t9", "name": "Ueno Park", "lat": 35.7146, "lng": 139.7732, "score": 72, "category": "nature", "why": "Museums, temples, and cherry blossoms", "rating": 4.4, "review_count": 9876},
        {"place_id": "t10", "name": "Tokyo Tower", "lat": 35.6586, "lng": 139.7454, "score": 70, "category": "landmark", "why": "Iconic red tower with city views", "rating": 4.3, "review_count": 31234},
        {"place_id": "t11", "name": "Harajuku", "lat": 35.6702, "lng": 139.7027, "score": 68, "category": "shopping", "why": "Youth fashion and quirky cafes", "rating": 4.1, "review_count": 8765},
        {"place_id": "t12", "name": "Imperial Palace", "lat": 35.6852, "lng": 139.7528, "score": 80, "category": "cultural", "why": "Historic residence of Japan's Imperial Family", "rating": 4.5, "review_count": 25678},
    ]
    
    # Hotel location
    hotel_coords = (35.6812, 139.7671)  # Tokyo Station
    
    # Run solver
    solver_output = solve_itinerary(
        places=scored_places,
        hotel_coords=hotel_coords,
        num_days=num_days,
        time_limit_seconds=10
    )
    
    # Format response for frontend
    response = format_itinerary_response(
        city=city,
        vibe=vibe,
        num_days=num_days,
        start_date=start_date,
        solver_output=solver_output,
        original_places=scored_places,
        hotel_coords=hotel_coords,
    )
    
    print("\nFRONTEND RESPONSE:")
    print(json.dumps(response, indent=2))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Success: {response['success']}")
    print(f"City: {response['trip']['city']}")
    print(f"Dates: {response['trip']['start_date']} to {response['trip']['end_date']}")
    print(f"Total Places: {response['trip']['total_places']}")
    print(f"Dropped: {response['trip']['places_dropped']}")
    
    for day in response['days']:
        if day['places']:
            print(f"\nDay {day['day_number']} ({day['date']}):")
            for p in day['places']:
                print(f"  {p['time']['arrival']} - {p['name']}")


def test_error_response():
    print("\n" + "="*60)
    print("ERROR RESPONSE TEST")
    print("="*60)
    
    error_response = format_error_response(
        error_message="Failed to generate places: API rate limit exceeded",
        city="Paris",
        vibe="romantic"
    )
    print(json.dumps(error_response, indent=2))


if __name__ == "__main__":
    test_full_pipeline()
    test_error_response()
