"""
Solver Module - Multi-Day Itinerary Optimization using OR-Tools
================================================================
Uses Vehicle Routing Problem (VRP) with the "Days as Vehicles" approach.
Each "vehicle" represents one day of the trip, all starting/ending at the hotel.

Key Concepts:
- num_vehicles = num_days (each day is a vehicle)
- depot = 0 (hotel/starting point)
- Time horizon = 720 minutes (12 hours per day)
- Prize Collecting TSP: Low-value places can be dropped if they don't fit

Author: go. travel planner
"""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import math


@dataclass
class ItineraryItem:
    """Represents a single stop in the itinerary."""
    place_id: str
    name: str
    lat: float
    lng: float
    arrival_time: int  # Minutes from day start
    departure_time: int  # Minutes from day start
    duration: int  # Visit duration in minutes
    score: float
    category: str
    why: str
    formatted_address: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "place_id": self.place_id,
            "name": self.name,
            "lat": self.lat,
            "lng": self.lng,
            "arrival_time": self.arrival_time,
            "arrival_time_formatted": self._format_time(self.arrival_time),
            "departure_time": self.departure_time,
            "departure_time_formatted": self._format_time(self.departure_time),
            "duration": self.duration,
            "score": self.score,
            "category": self.category,
            "why": self.why,
            "formatted_address": self.formatted_address,
        }
    
    @staticmethod
    def _format_time(minutes: int) -> str:
        """Convert minutes from midnight to HH:MM format."""
        hours = minutes // 60
        mins = minutes % 60
        period = "AM" if hours < 12 else "PM"
        display_hour = hours % 12
        if display_hour == 0:
            display_hour = 12
        return f"{display_hour}:{mins:02d} {period}"


@dataclass
class DayItinerary:
    """Represents one day's complete itinerary."""
    day_number: int
    items: List[ItineraryItem] = field(default_factory=list)
    total_travel_time: int = 0  # Minutes
    total_visit_time: int = 0  # Minutes
    total_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "day": self.day_number,
            "items": [item.to_dict() for item in self.items],
            "total_travel_time": self.total_travel_time,
            "total_visit_time": self.total_visit_time,
            "total_time": self.total_travel_time + self.total_visit_time,
            "total_score": round(self.total_score, 2),
            "num_places": len(self.items),
        }


class ItinerarySolver:
    """
    Multi-day itinerary optimizer using OR-Tools Vehicle Routing Problem.
    
    Approach: "Days as Vehicles"
    - Each day is modeled as a separate vehicle
    - All vehicles start and end at the depot (hotel)
    - Time dimension limits each day to ~12 hours
    - Prize Collecting: Low-priority places can be dropped
    """
    
    # Constants
    EARTH_RADIUS_KM: float = 6371.0
    AVERAGE_SPEED_KMH: float = 12.0  # Realistic transit speed (includes waiting, walking to/from stops)
    DAY_START_TIME: int = 540  # 9:00 AM in minutes from midnight
    DAY_END_TIME: int = 1320  # 10:00 PM in minutes from midnight
    MAX_DAY_DURATION: int = 780  # 13 hours in minutes (9 AM - 10 PM)
    DEFAULT_VISIT_DURATION: int = 60  # 1 hour default visit time
    
    # Visit durations by category (in minutes)
    VISIT_DURATIONS: Dict[str, int] = {
        "landmark": 45,
        "museum": 120,
        "restaurant": 75,
        "nature": 90,
        "nightlife": 120,
        "club": 120,
        "bar": 90,
        "shopping": 60,
        "cultural": 60,
        "cafe": 30,
        "breakfast": 45,
        "brunch": 60,
        "lunch": 60,
        "dinner": 90,
    }
    
    # Category-based preferred time windows (in minutes from midnight)
    # Format: (earliest_start, latest_start) - when the visit should BEGIN
    CATEGORY_TIME_WINDOWS: Dict[str, Tuple[int, int]] = {
        # Morning activities (9 AM - 12 PM start)
        "breakfast": (540, 660),      # 9:00 AM - 11:00 AM
        "brunch": (600, 780),          # 10:00 AM - 1:00 PM
        "cafe": (480, 1080),           # 8:00 AM - 6:00 PM (flexible)
        
        # Daytime activities (9 AM - 5 PM start)
        "museum": (540, 900),          # 9:00 AM - 3:00 PM (need time to visit)
        "landmark": (540, 1020),       # 9:00 AM - 5:00 PM
        "cultural": (540, 1020),       # 9:00 AM - 5:00 PM
        "nature": (540, 1020),         # 9:00 AM - 5:00 PM
        "shopping": (600, 1080),       # 10:00 AM - 6:00 PM
        
        # Meals
        "lunch": (720, 840),           # 12:00 PM - 2:00 PM
        "restaurant": (720, 1200),     # 12:00 PM - 8:00 PM (flexible for lunch/dinner)
        "dinner": (1080, 1260),        # 6:00 PM - 9:00 PM
        
        # Evening/Night activities (6 PM - 11 PM start)
        "nightlife": (1080, 1380),     # 6:00 PM - 11:00 PM
        "club": (1260, 1440),          # 9:00 PM - midnight
        "bar": (1080, 1380),           # 6:00 PM - 11:00 PM
    }
    
    def __init__(self):
        """Initialize the solver."""
        pass
    
    def haversine_distance(
        self, 
        lat1: float, 
        lng1: float, 
        lat2: float, 
        lng2: float
    ) -> float:
        """
        Calculate great-circle distance between two points in kilometers.
        
        Formula: d = 2R × arcsin(√(sin²(Δlat/2) + cos(lat1)cos(lat2)sin²(Δlng/2)))
        """
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) *
            math.sin(delta_lng / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return self.EARTH_RADIUS_KM * c
    
    def calculate_travel_time(
        self, 
        lat1: float, 
        lng1: float, 
        lat2: float, 
        lng2: float
    ) -> int:
        """
        Calculate travel time in minutes between two points.
        
        Uses Haversine distance and average city speed.
        Adds 5-minute buffer for parking/walking.
        """
        distance_km = self.haversine_distance(lat1, lng1, lat2, lng2)
        travel_hours = distance_km / self.AVERAGE_SPEED_KMH
        travel_minutes = int(travel_hours * 60)
        
        # Add buffer for orientation, finding entrances, etc.
        buffer = 10
        
        return travel_minutes + buffer
    
    def get_visit_duration(self, category: str) -> int:
        """Get estimated visit duration for a place category."""
        return self.VISIT_DURATIONS.get(category.lower(), self.DEFAULT_VISIT_DURATION)
    
    def get_time_window(
        self, 
        place: Dict[str, Any], 
        day_of_week: int = 1  # Default Monday (1=Monday in Google's format)
    ) -> Tuple[int, int]:
        """
        Calculate the time window for a place based on category and opening hours.
        
        Returns (earliest_start, latest_start) in minutes from midnight.
        The solver will use these as constraints for when the visit can BEGIN.
        
        Priority:
        1. Actual opening hours from Google Places (if available)
        2. Category-based preferred times
        3. Default day window (9 AM - 9 PM)
        """
        category = place.get("category", "").lower()
        opening_hours = place.get("opening_hours")
        visit_duration = self.get_visit_duration(category)
        
        # Start with category-based defaults
        if category in self.CATEGORY_TIME_WINDOWS:
            earliest, latest = self.CATEGORY_TIME_WINDOWS[category]
        else:
            # Default: can visit anytime during the day
            earliest = self.DAY_START_TIME  # 9 AM
            latest = self.DAY_END_TIME - visit_duration  # Need time to complete visit
        
        # Refine with actual opening hours if available
        if opening_hours and opening_hours.get("by_day"):
            by_day = opening_hours["by_day"]
            
            # Convert day_of_week: our input uses 0=Sunday, which matches Google
            if day_of_week in by_day:
                hours = by_day[day_of_week]
                place_opens = hours["open"]
                place_closes = hours["close"]
                
                # Constrain our window to actual opening hours
                # Can't start before it opens
                earliest = max(earliest, place_opens)
                # Must finish before it closes, so start no later than close - duration
                latest = min(latest, place_closes - visit_duration)
                
                # Ensure valid window
                if earliest > latest:
                    # Place doesn't fit in our preferred window - use opening hours directly
                    earliest = place_opens
                    latest = max(place_opens, place_closes - visit_duration)
        
        # Clamp to day boundaries
        earliest = max(earliest, self.DAY_START_TIME)
        latest = min(latest, self.DAY_END_TIME - visit_duration)
        latest = max(latest, earliest)  # Ensure latest >= earliest
        
        return (earliest, latest)
    
    def create_data_model(
        self,
        places: List[Dict[str, Any]],
        hotel_coords: Tuple[float, float],
        num_days: int = 1
    ) -> Dict[str, Any]:
        """
        Create the data model for OR-Tools routing solver.
        
        Args:
            places: List of place dicts with lat, lng, score, category
            hotel_coords: (lat, lng) tuple for the hotel/start point
            num_days: Number of days for the trip (becomes num_vehicles)
        
        Returns:
            Data model dict for OR-Tools
        """
        # Depot (index 0) is the hotel
        # Places are indices 1 to N
        num_locations = len(places) + 1  # +1 for depot
        
        # Build locations list: [depot, place1, place2, ...]
        locations = [(hotel_coords[0], hotel_coords[1])]  # Depot first
        for place in places:
            lat = place.get("lat") or hotel_coords[0]
            lng = place.get("lng") or hotel_coords[1]
            locations.append((lat, lng))
        
        # Build time matrix (travel times between all pairs)
        # time_matrix[i][j] = travel time from location i to location j
        time_matrix = []
        for i, (lat1, lng1) in enumerate(locations):
            row = []
            for j, (lat2, lng2) in enumerate(locations):
                if i == j:
                    row.append(0)
                else:
                    row.append(self.calculate_travel_time(lat1, lng1, lat2, lng2))
            time_matrix.append(row)
        
        # Build service times (visit duration at each location)
        # service_times[0] = 0 (no time spent at depot)
        service_times = [0]  # Depot
        for place in places:
            category = place.get("category", "landmark")
            service_times.append(self.get_visit_duration(category))
        
        # Build prizes (scores) for Prize Collecting TSP
        # Higher score = higher priority to visit
        # prizes[0] = 0 (depot has no prize)
        prizes = [0]  # Depot
        for place in places:
            # Scale score to integer (OR-Tools needs ints)
            score = place.get("score", 50.0)
            prizes.append(int(score * 10))  # Scale up for precision
        
        # Build penalty for NOT visiting (for Prize Collecting)
        # Lower penalty = more likely to be dropped
        # We want high-score places to have high penalty (don't want to drop them)
        penalties = [0]  # Depot (must be visited, no penalty)
        for place in places:
            score = place.get("score", 50.0)
            # Penalty proportional to score - dropping high-score places is expensive
            penalties.append(int(score * 10))
        
        # Build time windows for each location
        # time_windows[i] = (earliest_start, latest_start) in minutes from DAY_START
        # Depot can be visited anytime (start/end of day)
        time_windows = [(0, self.MAX_DAY_DURATION)]  # Depot
        for place in places:
            earliest, latest = self.get_time_window(place)
            # Convert from minutes-from-midnight to minutes-from-day-start
            earliest_relative = max(0, earliest - self.DAY_START_TIME)
            latest_relative = min(self.MAX_DAY_DURATION, latest - self.DAY_START_TIME)
            time_windows.append((earliest_relative, latest_relative))
        
        data = {
            "time_matrix": time_matrix,
            "service_times": service_times,
            "prizes": prizes,
            "penalties": penalties,
            "time_windows": time_windows,  # NEW: time window constraints
            "num_vehicles": num_days,  # DAYS AS VEHICLES
            "depot": 0,  # Hotel is the depot
            "num_locations": num_locations,
            "locations": locations,
            "places": places,  # Keep original place data
            "max_time_per_vehicle": self.MAX_DAY_DURATION,
        }
        
        return data
    
    def solve(
        self,
        places: List[Dict[str, Any]],
        hotel_coords: Optional[Tuple[float, float]] = None,
        num_days: int = 1,
        time_limit_seconds: int = 10
    ) -> List[DayItinerary]:
        """
        Solve the multi-day itinerary optimization problem.
        
        Args:
            places: List of place dicts (must have lat, lng, score, category)
            hotel_coords: (lat, lng) for hotel. If None, uses centroid of places.
            num_days: Number of days for the trip
            time_limit_seconds: Max solver time
        
        Returns:
            List of DayItinerary objects, one per day
        """
        if not places:
            return [DayItinerary(day_number=i+1) for i in range(num_days)]
        
        # Filter places with valid coordinates
        valid_places = [
            p for p in places 
            if p.get("lat") is not None and p.get("lng") is not None
        ]
        
        if not valid_places:
            return [DayItinerary(day_number=i+1) for i in range(num_days)]
        
        # Calculate hotel coords (centroid) if not provided
        if hotel_coords is None:
            avg_lat = sum(p["lat"] for p in valid_places) / len(valid_places)
            avg_lng = sum(p["lng"] for p in valid_places) / len(valid_places)
            hotel_coords = (avg_lat, avg_lng)
        
        # Create data model
        data = self.create_data_model(valid_places, hotel_coords, num_days)
        
        # Create routing index manager
        # Nodes: 0 = depot, 1..N = places
        manager = pywrapcp.RoutingIndexManager(
            data["num_locations"],
            data["num_vehicles"],
            data["depot"]
        )
        
        # Create routing model
        routing = pywrapcp.RoutingModel(manager)
        
        # ----- TIME DIMENSION -----
        # Callback for time: travel time + service time at destination
        # This way CumulVar represents "completion time" at each node
        def time_callback(from_index, to_index):
            """Returns travel time + service time at destination."""
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            travel_time = data["time_matrix"][from_node][to_node]
            service_time = data["service_times"][to_node]
            return travel_time + service_time
        
        transit_callback_index = routing.RegisterTransitCallback(time_callback)
        
        # Set cost to minimize total time
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Add Time dimension
        # This constrains each vehicle (day) to MAX_DAY_DURATION
        routing.AddDimension(
            transit_callback_index,
            120,  # Allow 2 hour slack (waiting time for time windows)
            data["max_time_per_vehicle"],  # Max time per vehicle
            True,  # Start cumul at zero (each day starts fresh)
            "Time"
        )
        time_dimension = routing.GetDimensionOrDie("Time")
        
        # ----- TIME WINDOW CONSTRAINTS -----
        # Apply time windows to each node (except depot which is flexible)
        for node in range(1, data["num_locations"]):  # Skip depot (node 0)
            index = manager.NodeToIndex(node)
            earliest, latest = data["time_windows"][node]
            time_dimension.CumulVar(index).SetRange(earliest, latest)
        
        # Minimize total time across all days
        for vehicle_id in range(data["num_vehicles"]):
            time_dimension.SetSpanCostCoefficientForVehicle(1, vehicle_id)
        
        # ----- PRIZE COLLECTING (Allow Dropping Nodes) -----
        # Add disjunctions - each place can be visited OR dropped (with penalty)
        for node in range(1, data["num_locations"]):  # Skip depot
            index = manager.NodeToIndex(node)
            # Penalty for NOT visiting this node
            # Higher penalty = solver tries harder to include it
            penalty = data["penalties"][node]
            routing.AddDisjunction([index], penalty)
        
        # ----- SOLVER SETTINGS -----
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = time_limit_seconds
        
        # Solve
        solution = routing.SolveWithParameters(search_parameters)
        
        # Extract solution
        if solution:
            return self._extract_solution(data, manager, routing, solution)
        else:
            # No solution found - return empty days
            print("WARNING: No solution found by OR-Tools solver")
            return [DayItinerary(day_number=i+1) for i in range(num_days)]
    
    def _extract_solution(
        self,
        data: Dict[str, Any],
        manager: pywrapcp.RoutingIndexManager,
        routing: pywrapcp.RoutingModel,
        solution: pywrapcp.Assignment
    ) -> List[DayItinerary]:
        """
        Extract the solution from OR-Tools into DayItinerary objects.
        
        Each vehicle (day) gets its own itinerary.
        """
        time_dimension = routing.GetDimensionOrDie("Time")
        days = []
        
        for vehicle_id in range(data["num_vehicles"]):
            day = DayItinerary(day_number=vehicle_id + 1)
            
            index = routing.Start(vehicle_id)
            previous_index = index
            
            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                time_var = time_dimension.CumulVar(index)
                cumul_time = solution.Value(time_var)
                
                # Skip depot (node 0)
                if node != 0:
                    # Get place data (node - 1 because depot is 0)
                    place = data["places"][node - 1]
                    
                    duration = data["service_times"][node]
                    
                    # CumulVar includes service time, so we need to subtract it
                    # to get the actual arrival time
                    # cumul_time = time when we FINISH at this location
                    # arrival_time = cumul_time - duration (when we ARRIVE)
                    arrival_time = cumul_time - duration
                    departure_time = cumul_time
                    
                    item = ItineraryItem(
                        place_id=place.get("place_id", f"place_{node}"),
                        name=place.get("name", f"Place {node}"),
                        lat=place.get("lat", 0),
                        lng=place.get("lng", 0),
                        arrival_time=self.DAY_START_TIME + arrival_time,
                        departure_time=self.DAY_START_TIME + departure_time,
                        duration=duration,
                        score=place.get("score", 0),
                        category=place.get("category", ""),
                        why=place.get("why", ""),
                        formatted_address=place.get("formatted_address"),
                    )
                    
                    day.items.append(item)
                    day.total_visit_time += duration
                    day.total_score += place.get("score", 0)
                    
                    # Calculate travel time from previous location
                    if previous_index != routing.Start(vehicle_id):
                        prev_node = manager.IndexToNode(previous_index)
                        travel_time = data["time_matrix"][prev_node][node]
                        day.total_travel_time += travel_time
                
                previous_index = index
                index = solution.Value(routing.NextVar(index))
            
            days.append(day)
        
        return days


def solve_itinerary(
    places: List[Dict[str, Any]],
    hotel_coords: Optional[Tuple[float, float]] = None,
    num_days: int = 1,
    time_limit_seconds: int = 10
) -> List[Dict[str, Any]]:
    """
    Convenience function to solve itinerary and return dicts.
    
    Args:
        places: List of place dicts
        hotel_coords: Optional (lat, lng) for hotel
        num_days: Number of days
        time_limit_seconds: Solver time limit
    
    Returns:
        List of day dicts with items
    """
    solver = ItinerarySolver()
    day_itineraries = solver.solve(places, hotel_coords, num_days, time_limit_seconds)
    return [day.to_dict() for day in day_itineraries]


# For testing
if __name__ == "__main__":
    import json
    
    # Sample places with various categories including nightlife
    test_places = [
        {"name": "Vancouver Aquarium", "lat": 49.3005, "lng": -123.1309, "score": 85.0, "category": "landmark", "why": "Marine life", "place_id": "1"},
        {"name": "Stanley Park", "lat": 49.3017, "lng": -123.1417, "score": 92.0, "category": "nature", "why": "Urban park", "place_id": "2"},
        {"name": "Granville Island", "lat": 49.2712, "lng": -123.1340, "score": 78.0, "category": "shopping", "why": "Market", "place_id": "3"},
        {"name": "Gastown", "lat": 49.2838, "lng": -123.1088, "score": 70.0, "category": "cultural", "why": "Historic", "place_id": "4"},
        {"name": "Science World", "lat": 49.2734, "lng": -123.1038, "score": 75.0, "category": "museum", "why": "Science museum", "place_id": "5"},
        {"name": "Capilano Bridge", "lat": 49.3429, "lng": -123.1149, "score": 88.0, "category": "nature", "why": "Suspension bridge", "place_id": "6"},
        # Nightlife - should be scheduled in evening
        {"name": "Celebrities Nightclub", "lat": 49.2820, "lng": -123.1171, "score": 72.0, "category": "club", "why": "Popular nightclub", "place_id": "7"},
        {"name": "The Keefer Bar", "lat": 49.2803, "lng": -123.1045, "score": 68.0, "category": "bar", "why": "Craft cocktails", "place_id": "8"},
        # Meals
        {"name": "Medina Cafe", "lat": 49.2808, "lng": -123.1139, "score": 80.0, "category": "breakfast", "why": "Best brunch spot", "place_id": "9"},
        {"name": "Miku Restaurant", "lat": 49.2876, "lng": -123.1134, "score": 85.0, "category": "dinner", "why": "Fine dining sushi", "place_id": "10"},
        # Museum with opening hours
        {"name": "Museum of Anthropology", "lat": 49.2695, "lng": -123.2590, "score": 80.0, "category": "museum", "why": "Cultural artifacts", "place_id": "11",
         "opening_hours": {"by_day": {1: {"open": 600, "close": 1020}}}},  # 10 AM - 5 PM Monday
    ]
    
    # Hotel at downtown Vancouver
    hotel = (49.2827, -123.1207)
    
    print("="*60)
    print("TIME-AWARE ITINERARY SOLVER TEST")
    print("="*60)
    print(f"Places: {len(test_places)}")
    print(f"Hotel: {hotel}")
    print("\nExpected behavior:")
    print("- Museums: 9 AM - 3 PM start")
    print("- Breakfast: 9 AM - 11 AM")
    print("- Dinner: 6 PM - 9 PM")
    print("- Clubs: 9 PM - midnight")
    print("- Bars: 6 PM - 11 PM")
    
    # Test: 2 days - should have morning/day activities then evening ones
    print("\n--- TEST: 2 Days with Time Constraints ---")
    result = solve_itinerary(test_places, hotel, num_days=2)
    for day in result:
        print(f"\nDay {day['day']}: {day['num_places']} places, Score: {day['total_score']}")
        for item in day['items']:
            print(f"  {item['arrival_time_formatted']} - {item['departure_time_formatted']} | {item['name']} ({item['category']})")
