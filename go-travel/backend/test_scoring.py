"""
Comprehensive Scoring Test
===========================
Tests the scoring system across multiple cities with real weather data.
"""

import json
from weather import fetch_weather_sync
from scoring import UtilityScorer, rank_places

def test_scoring():
    scorer = UtilityScorer()
    
    # Test cities with different weather conditions
    cities = ["Vancouver", "Tokyo", "Paris", "London", "Sydney", "New York"]
    
    for city in cities:
        print(f"\n{'='*60}")
        print(f"CITY: {city}")
        print('='*60)
        
        # Fetch real weather
        weather = fetch_weather_sync(city)
        if weather:
            print(f"Weather: {weather['main']} ({weather['description']})")
            print(f"Temperature: {weather['temp']}°C (feels like {weather['feels_like']}°C)")
            print(f"Humidity: {weather['humidity']}%")
        else:
            print("Weather: Unable to fetch")
            weather = None
        
        # Create test places for this city
        test_places = [
            {
                "name": f"{city} Central Park",
                "lat": 49.3 + cities.index(city) * 0.1,
                "lng": -123.1,
                "types": ["park", "tourist_attraction"],
                "rating": 4.7,
                "user_ratings_total": 25000,
                "category": "nature",
                "why": "Beautiful urban park."
            },
            {
                "name": f"{city} Art Museum",
                "lat": 49.3 + cities.index(city) * 0.1,
                "lng": -123.11,
                "types": ["museum", "tourist_attraction"],
                "rating": 4.6,
                "user_ratings_total": 15000,
                "category": "museum",
                "why": "World-class art collection."
            },
            {
                "name": f"{city} Zoo",
                "lat": 49.31 + cities.index(city) * 0.1,
                "lng": -123.12,
                "types": ["zoo", "tourist_attraction"],
                "rating": 4.4,
                "user_ratings_total": 8000,
                "category": "nature",
                "why": "Amazing wildlife exhibits."
            },
            {
                "name": f"{city} Famous Restaurant",
                "lat": 49.3 + cities.index(city) * 0.1,
                "lng": -123.1,
                "types": ["restaurant"],
                "rating": 4.8,
                "user_ratings_total": 5000,
                "category": "restaurant",
                "why": "Michelin-starred dining."
            },
            {
                "name": f"{city} Hidden Gem Cafe",
                "lat": 49.3 + cities.index(city) * 0.1,
                "lng": -123.1,
                "types": ["cafe"],
                "rating": 4.9,
                "user_ratings_total": 50,  # Few reviews
                "category": "restaurant",
                "why": "Local favorite, few tourists."
            },
            {
                "name": f"{city} Beach",
                "lat": 49.35 + cities.index(city) * 0.1,  # 5km away
                "lng": -123.15,
                "types": ["beach", "natural_feature"],
                "rating": 4.5,
                "user_ratings_total": 12000,
                "category": "nature",
                "why": "Beautiful sandy beach."
            },
            {
                "name": f"{city} Shopping Mall",
                "lat": 49.3 + cities.index(city) * 0.1,
                "lng": -123.1,
                "types": ["shopping_mall"],
                "rating": 4.2,
                "user_ratings_total": 3000,
                "category": "shopping",
                "why": "Premium shopping experience."
            },
            {
                "name": f"{city} Historic Temple",
                "lat": 49.32 + cities.index(city) * 0.1,
                "lng": -123.13,
                "types": ["place_of_worship", "tourist_attraction"],
                "rating": 4.6,
                "user_ratings_total": 20000,
                "category": "cultural",
                "why": "Ancient cultural landmark."
            },
        ]
        
        # Rank places
        ranked = rank_places(test_places, weather=weather)
        
        print(f"\n{'Place':<30} {'Type':<15} {'Rating':<8} {'Reviews':<10} {'Score':<8} {'Notes'}")
        print("-" * 100)
        
        for place in ranked:
            place_type = place['category']
            rating = place['rating']
            reviews = place['user_ratings_total']
            score = place['score']
            
            # Determine notes
            notes = []
            if reviews >= 1000:
                notes.append("+10 social")
            if place_type in ['nature', 'park'] and weather and weather.get('main') in ['Rain', 'Drizzle']:
                notes.append("rain penalty")
            if place_type in ['nature', 'park'] and weather and weather.get('temp', 20) < 5:
                notes.append("cold penalty")
            
            notes_str = ", ".join(notes) if notes else "-"
            
            print(f"{place['name']:<30} {place_type:<15} {rating:<8} {reviews:<10} {score:<8} {notes_str}")
        
        # Show filtered out places
        original_names = {p['name'] for p in test_places}
        ranked_names = {p['name'] for p in ranked}
        filtered_out = original_names - ranked_names
        
        if filtered_out:
            print(f"\n⚠️  Filtered out (score < 40): {', '.join(filtered_out)}")


def test_rain_scenario():
    """Test with forced rain to see outdoor penalties"""
    print("\n" + "="*60)
    print("SPECIAL TEST: Simulated RAIN scenario")
    print("="*60)
    
    # Simulate rainy weather
    rain_weather = {"main": "Rain", "temp": 8.0, "description": "light rain"}
    print(f"Weather: {rain_weather['main']} ({rain_weather['description']})")
    print(f"Temperature: {rain_weather['temp']}°C")
    
    test_places = [
        {
            "name": "Stanley Park (OUTDOOR)",
            "lat": 49.3017, "lng": -123.1417,
            "types": ["park", "tourist_attraction"],
            "rating": 4.8, "user_ratings_total": 50000,
            "category": "nature", "why": "Beautiful park."
        },
        {
            "name": "Vancouver Aquarium (INDOOR)",
            "lat": 49.3005, "lng": -123.1309,
            "types": ["aquarium", "tourist_attraction"],
            "rating": 4.5, "user_ratings_total": 15000,
            "category": "landmark", "why": "Marine exhibits."
        },
        {
            "name": "Capilano Bridge (OUTDOOR)",
            "lat": 49.3429, "lng": -123.1149,
            "types": ["park", "tourist_attraction"],
            "rating": 4.6, "user_ratings_total": 30000,
            "category": "nature", "why": "Suspension bridge."
        },
        {
            "name": "Science World (INDOOR)",
            "lat": 49.2734, "lng": -123.1038,
            "types": ["museum", "tourist_attraction"],
            "rating": 4.5, "user_ratings_total": 12000,
            "category": "museum", "why": "Interactive exhibits."
        },
    ]
    
    ranked = rank_places(test_places, weather=rain_weather)
    
    print(f"\n{'Place':<35} {'Type':<12} {'Rating':<8} {'Score':<8} {'Rain Effect'}")
    print("-" * 90)
    
    for place in ranked:
        is_outdoor = place['category'] in ['nature', 'park']
        rain_effect = "70% PENALTY ☔" if is_outdoor else "No penalty ✓"
        print(f"{place['name']:<35} {place['category']:<12} {place['rating']:<8} {place['score']:<8} {rain_effect}")


def test_cold_scenario():
    """Test with cold weather"""
    print("\n" + "="*60)
    print("SPECIAL TEST: Simulated COLD scenario (2°C)")
    print("="*60)
    
    cold_weather = {"main": "Clear", "temp": 2.0, "description": "clear sky"}
    print(f"Weather: {cold_weather['main']} ({cold_weather['description']})")
    print(f"Temperature: {cold_weather['temp']}°C")
    
    test_places = [
        {
            "name": "Beach Walk (OUTDOOR)",
            "lat": 49.3, "lng": -123.1,
            "types": ["beach", "natural_feature"],
            "rating": 4.5, "user_ratings_total": 8000,
            "category": "nature", "why": "Scenic beach."
        },
        {
            "name": "Cozy Coffee Shop (INDOOR)",
            "lat": 49.3, "lng": -123.1,
            "types": ["cafe"],
            "rating": 4.6, "user_ratings_total": 500,
            "category": "restaurant", "why": "Great coffee."
        },
    ]
    
    ranked = rank_places(test_places, weather=cold_weather)
    
    print(f"\n{'Place':<35} {'Type':<12} {'Rating':<8} {'Score':<8} {'Cold Effect'}")
    print("-" * 90)
    
    for place in ranked:
        is_outdoor = place['category'] in ['nature', 'park']
        cold_effect = "50% PENALTY 🥶" if is_outdoor else "No penalty ✓"
        print(f"{place['name']:<35} {place['category']:<12} {place['rating']:<8} {place['score']:<8} {cold_effect}")


if __name__ == "__main__":
    test_scoring()
    test_rain_scenario()
    test_cold_scenario()
