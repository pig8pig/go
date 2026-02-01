"""
Comprehensive tests for the Multi-Day Itinerary Solver
"""
from solver import solve_itinerary

def test_many_places_few_days():
    """15 places, 2 days - should drop some"""
    print("="*60)
    print("TEST 1: 15 places, 2 days (should drop some)")
    print("="*60)
    many_places = [
        {"name": f"Place {i}", "lat": 49.28 + (i*0.01), "lng": -123.12 + (i*0.01), 
         "score": 60 + i*2, "category": "museum", "why": "test", "place_id": str(i)}
        for i in range(15)
    ]
    result = solve_itinerary(many_places, (49.28, -123.12), num_days=2)
    visited = sum(d["num_places"] for d in result)
    print(f"Visited: {visited}/15 places, Dropped: {15 - visited}")
    for day in result:
        print(f"  Day {day['day']}: {day['num_places']} places, {day['total_time']} min, Score: {day['total_score']}")

def test_heavy_dropping():
    """20 places, 1 day - heavy dropping expected"""
    print()
    print("="*60)
    print("TEST 2: 20 places, 1 day (heavy dropping expected)")
    print("="*60)
    lots_of_places = [
        {"name": f"Spot {i}", "lat": 49.25 + (i*0.008), "lng": -123.15 + (i*0.008),
         "score": 50 + i*2.5, "category": "landmark", "why": "test", "place_id": str(i)}
        for i in range(20)
    ]
    result = solve_itinerary(lots_of_places, (49.28, -123.12), num_days=1)
    visited = sum(d["num_places"] for d in result)
    print(f"Visited: {visited}/20 places, Dropped: {20 - visited}")
    for day in result:
        print(f"  Day {day['day']}: {day['num_places']} places, Score: {day['total_score']}")
        for item in day["items"][:3]:
            print(f"    {item['arrival_time_formatted']} - {item['name']} (score: {item['score']})")
        if len(day["items"]) > 3:
            print(f"    ... and {len(day['items'])-3} more")

def test_tokyo_weekend():
    """Tokyo 3-day trip with mixed categories"""
    print()
    print("="*60)
    print("TEST 3: Tokyo Weekend (3 days, 12 places)")
    print("="*60)
    tokyo_places = [
        {"name": "Senso-ji Temple", "lat": 35.7148, "lng": 139.7967, "score": 95, "category": "landmark", "why": "Historic temple", "place_id": "t1"},
        {"name": "Tokyo Skytree", "lat": 35.7101, "lng": 139.8107, "score": 88, "category": "landmark", "why": "Observation tower", "place_id": "t2"},
        {"name": "Shibuya Crossing", "lat": 35.6595, "lng": 139.7004, "score": 82, "category": "landmark", "why": "Famous crossing", "place_id": "t3"},
        {"name": "Meiji Shrine", "lat": 35.6764, "lng": 139.6993, "score": 90, "category": "cultural", "why": "Shinto shrine", "place_id": "t4"},
        {"name": "teamLab Borderless", "lat": 35.6264, "lng": 139.7841, "score": 92, "category": "museum", "why": "Digital art", "place_id": "t5"},
        {"name": "Tsukiji Outer Market", "lat": 35.6654, "lng": 139.7707, "score": 85, "category": "shopping", "why": "Food market", "place_id": "t6"},
        {"name": "Shinjuku Gyoen", "lat": 35.6852, "lng": 139.7100, "score": 78, "category": "nature", "why": "Garden", "place_id": "t7"},
        {"name": "Akihabara", "lat": 35.7023, "lng": 139.7745, "score": 75, "category": "shopping", "why": "Electronics", "place_id": "t8"},
        {"name": "Ueno Park", "lat": 35.7146, "lng": 139.7732, "score": 72, "category": "nature", "why": "Park with museums", "place_id": "t9"},
        {"name": "Tokyo Tower", "lat": 35.6586, "lng": 139.7454, "score": 70, "category": "landmark", "why": "Iconic tower", "place_id": "t10"},
        {"name": "Harajuku", "lat": 35.6702, "lng": 139.7027, "score": 68, "category": "shopping", "why": "Fashion district", "place_id": "t11"},
        {"name": "Imperial Palace", "lat": 35.6852, "lng": 139.7528, "score": 80, "category": "cultural", "why": "Royal residence", "place_id": "t12"},
    ]
    hotel = (35.6812, 139.7671)  # Tokyo Station area
    result = solve_itinerary(tokyo_places, hotel, num_days=3)
    visited = sum(d["num_places"] for d in result)
    print(f"Visited: {visited}/12 places")
    for day in result:
        print(f"\nDay {day['day']}: {day['num_places']} places, Score: {day['total_score']}")
        for item in day["items"]:
            print(f"  {item['arrival_time_formatted']} - {item['departure_time_formatted']}: {item['name']}")

def test_edge_cases():
    """Edge cases: empty, single place"""
    print()
    print("="*60)
    print("TEST 4: Edge cases")
    print("="*60)
    
    # Empty
    result = solve_itinerary([], (49.28, -123.12), num_days=2)
    print(f"Empty input: {len(result)} days returned, all empty: {all(d['num_places'] == 0 for d in result)}")
    
    # Single place
    single = [{"name": "Eiffel Tower", "lat": 48.8584, "lng": 2.2945, "score": 99, "category": "landmark", "why": "Iconic", "place_id": "e1"}]
    result = solve_itinerary(single, (48.8566, 2.3522), num_days=1)
    print(f"Single place: visited {result[0]['num_places']} - {result[0]['items'][0]['name'] if result[0]['items'] else 'none'}")

def test_week_trip():
    """7 days with 25 places - long trip"""
    print()
    print("="*60)
    print("TEST 5: Week-long trip (7 days, 25 places)")
    print("="*60)
    paris_places = [
        {"name": "Eiffel Tower", "lat": 48.8584, "lng": 2.2945, "score": 98, "category": "landmark", "why": "Iconic", "place_id": "p1"},
        {"name": "Louvre Museum", "lat": 48.8606, "lng": 2.3376, "score": 96, "category": "museum", "why": "Art museum", "place_id": "p2"},
        {"name": "Notre-Dame", "lat": 48.8530, "lng": 2.3499, "score": 92, "category": "landmark", "why": "Cathedral", "place_id": "p3"},
        {"name": "Sacre-Coeur", "lat": 48.8867, "lng": 2.3431, "score": 88, "category": "landmark", "why": "Basilica", "place_id": "p4"},
        {"name": "Arc de Triomphe", "lat": 48.8738, "lng": 2.2950, "score": 85, "category": "landmark", "why": "Monument", "place_id": "p5"},
        {"name": "Musee d'Orsay", "lat": 48.8600, "lng": 2.3266, "score": 90, "category": "museum", "why": "Impressionist art", "place_id": "p6"},
        {"name": "Champs-Elysees", "lat": 48.8698, "lng": 2.3075, "score": 80, "category": "shopping", "why": "Avenue", "place_id": "p7"},
        {"name": "Montmartre", "lat": 48.8867, "lng": 2.3338, "score": 82, "category": "cultural", "why": "Artist quarter", "place_id": "p8"},
        {"name": "Luxembourg Gardens", "lat": 48.8462, "lng": 2.3372, "score": 75, "category": "nature", "why": "Park", "place_id": "p9"},
        {"name": "Pantheon", "lat": 48.8462, "lng": 2.3461, "score": 72, "category": "landmark", "why": "Monument", "place_id": "p10"},
        {"name": "Centre Pompidou", "lat": 48.8606, "lng": 2.3522, "score": 78, "category": "museum", "why": "Modern art", "place_id": "p11"},
        {"name": "Tuileries Garden", "lat": 48.8634, "lng": 2.3275, "score": 70, "category": "nature", "why": "Garden", "place_id": "p12"},
        {"name": "Palace of Versailles", "lat": 48.8049, "lng": 2.1204, "score": 95, "category": "museum", "why": "Royal palace", "place_id": "p13"},
        {"name": "Sainte-Chapelle", "lat": 48.8554, "lng": 2.3450, "score": 85, "category": "landmark", "why": "Gothic chapel", "place_id": "p14"},
        {"name": "Rodin Museum", "lat": 48.8553, "lng": 2.3160, "score": 76, "category": "museum", "why": "Sculpture", "place_id": "p15"},
        {"name": "Le Marais", "lat": 48.8566, "lng": 2.3622, "score": 74, "category": "cultural", "why": "Historic district", "place_id": "p16"},
        {"name": "Latin Quarter", "lat": 48.8505, "lng": 2.3475, "score": 72, "category": "cultural", "why": "Student area", "place_id": "p17"},
        {"name": "Opera Garnier", "lat": 48.8720, "lng": 2.3316, "score": 80, "category": "cultural", "why": "Opera house", "place_id": "p18"},
        {"name": "Palais Royal", "lat": 48.8638, "lng": 2.3373, "score": 68, "category": "landmark", "why": "Palace", "place_id": "p19"},
        {"name": "Invalides", "lat": 48.8567, "lng": 2.3126, "score": 77, "category": "museum", "why": "Military museum", "place_id": "p20"},
        {"name": "Catacombs", "lat": 48.8339, "lng": 2.3325, "score": 82, "category": "museum", "why": "Underground", "place_id": "p21"},
        {"name": "Pere Lachaise", "lat": 48.8614, "lng": 2.3932, "score": 70, "category": "nature", "why": "Cemetery", "place_id": "p22"},
        {"name": "Moulin Rouge", "lat": 48.8842, "lng": 2.3322, "score": 75, "category": "nightlife", "why": "Cabaret", "place_id": "p23"},
        {"name": "Seine River Cruise", "lat": 48.8584, "lng": 2.2945, "score": 83, "category": "nature", "why": "Boat tour", "place_id": "p24"},
        {"name": "Galeries Lafayette", "lat": 48.8737, "lng": 2.3317, "score": 65, "category": "shopping", "why": "Department store", "place_id": "p25"},
    ]
    hotel = (48.8566, 2.3522)  # Central Paris
    result = solve_itinerary(paris_places, hotel, num_days=7, time_limit_seconds=15)
    visited = sum(d["num_places"] for d in result)
    print(f"Visited: {visited}/25 places")
    total_score = sum(d["total_score"] for d in result)
    print(f"Total trip score: {total_score}")
    for day in result:
        if day["num_places"] > 0:
            names = [item["name"] for item in day["items"]]
            print(f"  Day {day['day']}: {day['num_places']} places - {', '.join(names[:3])}{'...' if len(names) > 3 else ''}")

if __name__ == "__main__":
    test_many_places_few_days()
    test_heavy_dropping()
    test_tokyo_weekend()
    test_edge_cases()
    test_week_trip()
    print("\n" + "="*60)
    print("ALL TESTS COMPLETE")
    print("="*60)
