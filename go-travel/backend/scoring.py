"""
Scoring Module - Utility Score Calculator for Travel Recommendations
=====================================================================
This module implements a Weighted Utility Function to rank candidate places
based on multiple real-world factors: distance, weather, ratings, and popularity.

Author: go. travel planner
"""

import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CandidatePlace:
    """Represents a candidate place with all relevant attributes."""
    name: str
    lat: Optional[float]
    lng: Optional[float]
    types: List[str]
    rating: Optional[float]
    user_ratings_total: Optional[int]
    category: str
    why: str
    place_id: Optional[str] = None
    formatted_address: Optional[str] = None
    photo_url: Optional[str] = None
    score: float = 0.0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CandidatePlace":
        """Create a CandidatePlace from a dictionary."""
        return cls(
            name=data.get("name", ""),
            lat=data.get("lat"),
            lng=data.get("lng"),
            types=data.get("types", []),
            rating=data.get("rating"),
            user_ratings_total=data.get("user_ratings_total"),
            category=data.get("category", ""),
            why=data.get("why", ""),
            place_id=data.get("place_id"),
            formatted_address=data.get("formatted_address"),
            photo_url=data.get("photo_url"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert back to dictionary for API response."""
        return {
            "name": self.name,
            "lat": self.lat,
            "lng": self.lng,
            "types": self.types,
            "rating": self.rating,
            "user_ratings_total": self.user_ratings_total,
            "category": self.category,
            "why": self.why,
            "place_id": self.place_id,
            "formatted_address": self.formatted_address,
            "photo_url": self.photo_url,
            "score": round(self.score, 2),
        }


class UtilityScorer:
    """
    Calculates utility scores for candidate places using a weighted multi-factor model.
    
    The scoring function combines:
    1. Base quality score (from Google ratings)
    2. Spatial decay (penalizes distant places)
    3. Weather compatibility (penalizes outdoor places in bad weather)
    4. Social proof boost (rewards highly-reviewed places)
    
    Final scores range from 0.0 to 100.0+
    """
    
    # Earth's radius in kilometers (for Haversine formula)
    EARTH_RADIUS_KM: float = 6371.0
    
    # Decay constant for distance penalty
    # At 10km, multiplier ≈ 0.61 (39% penalty)
    # At 5km, multiplier ≈ 0.78 (22% penalty)
    # At 20km, multiplier ≈ 0.37 (63% penalty)
    DISTANCE_DECAY_RATE: float = 0.05
    
    # Minimum score threshold - places below this are filtered out
    MIN_SCORE_THRESHOLD: float = 40.0
    
    # Outdoor place types that are affected by weather
    OUTDOOR_TYPES: set = {
        "park", "zoo", "amusement_park", "campground", "stadium",
        "natural_feature", "hiking_area", "beach", "garden",
        "nature", "outdoor"  # Including our custom categories
    }
    
    # Weather conditions that penalize outdoor activities
    BAD_WEATHER_CONDITIONS: set = {"Rain", "Drizzle", "Thunderstorm", "Snow"}
    
    def __init__(self):
        """Initialize the UtilityScorer with default parameters."""
        pass
    
    def haversine_distance(
        self, 
        lat1: float, 
        lng1: float, 
        lat2: float, 
        lng2: float
    ) -> float:
        """
        Calculate the great-circle distance between two points on Earth.
        
        Uses the Haversine formula:
        a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlng/2)
        c = 2 * atan2(√a, √(1-a))
        d = R * c
        
        Args:
            lat1, lng1: Coordinates of point 1 (in degrees)
            lat2, lng2: Coordinates of point 2 (in degrees)
        
        Returns:
            Distance in kilometers
        """
        # Convert degrees to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        # Haversine formula
        # a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlng/2)
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * 
            math.sin(delta_lng / 2) ** 2
        )
        
        # c = 2 * atan2(√a, √(1-a))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        # d = R * c
        distance_km = self.EARTH_RADIUS_KM * c
        
        return distance_km
    
    def calculate_base_score(self, rating: Optional[float]) -> float:
        """
        Calculate base score from Google rating.
        
        Normalizes the 0-5 star rating to a 0-100 scale.
        Formula: score = rating * 20
        
        Args:
            rating: Google Places rating (0.0 to 5.0)
        
        Returns:
            Base score (0.0 to 100.0)
        """
        if rating is None:
            # Default to average rating if unknown
            return 60.0  # Equivalent to 3.0 stars
        
        # Clamp rating to valid range
        rating = max(0.0, min(5.0, rating))
        
        return rating * 20.0
    
    def calculate_distance_multiplier(
        self, 
        place_lat: Optional[float], 
        place_lng: Optional[float],
        centroid_lat: float,
        centroid_lng: float
    ) -> float:
        """
        Calculate spatial decay multiplier based on distance from centroid.
        
        Uses exponential decay: multiplier = e^(-k * distance)
        where k = 0.15 (decay rate constant)
        
        Effect at various distances:
        - 0 km:  multiplier = 1.00 (no penalty)
        - 2 km:  multiplier = 0.74 (26% penalty)
        - 5 km:  multiplier = 0.47 (53% penalty)
        - 10 km: multiplier = 0.22 (78% penalty)
        - 20 km: multiplier = 0.05 (95% penalty)
        
        Args:
            place_lat, place_lng: Coordinates of the place
            centroid_lat, centroid_lng: Coordinates of trip centroid
        
        Returns:
            Multiplier between 0.0 and 1.0
        """
        if place_lat is None or place_lng is None:
            # No coordinates - apply moderate penalty
            return 0.5
        
        distance_km = self.haversine_distance(
            place_lat, place_lng,
            centroid_lat, centroid_lng
        )
        
        # Exponential decay: e^(-k * d)
        # This creates a smooth falloff where nearby places are preferred
        multiplier = math.exp(-self.DISTANCE_DECAY_RATE * distance_km)
        
        return multiplier
    
    def calculate_weather_multiplier(
        self,
        place_types: List[str],
        place_category: str,
        weather: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate weather compatibility multiplier.
        
        Penalizes outdoor places during inclement weather:
        - Rain/Drizzle + outdoor: 0.3 multiplier (70% penalty)
        - Cold (<5°C) + outdoor: 0.5 multiplier (50% penalty)
        - Good weather or indoor: 1.0 multiplier (no penalty)
        
        Args:
            place_types: List of Google place types
            place_category: Our custom category (nature, landmark, etc.)
            weather: Dict with 'main' (condition) and 'temp' (celsius)
        
        Returns:
            Multiplier between 0.3 and 1.0
        """
        if weather is None:
            # No weather data - no penalty
            return 1.0
        
        # Check if place is outdoor
        is_outdoor = any(
            t.lower() in self.OUTDOOR_TYPES 
            for t in place_types + [place_category]
        )
        
        if not is_outdoor:
            # Indoor place - no weather penalty
            return 1.0
        
        # Get weather conditions
        main_condition = weather.get("main", "").strip()
        temp_celsius = weather.get("temp", 20.0)  # Default to comfortable temp
        
        multiplier = 1.0
        
        # Heavy penalty for rain/drizzle on outdoor activities
        if main_condition in self.BAD_WEATHER_CONDITIONS:
            multiplier *= 0.3
        
        # Moderate penalty for cold weather on outdoor activities
        if temp_celsius < 5.0:
            multiplier *= 0.5
        
        return multiplier
    
    def calculate_social_proof_bonus(
        self, 
        user_ratings_total: Optional[int]
    ) -> float:
        """
        Calculate social proof bonus based on review count.
        
        Places with many reviews are more reliable indicators of quality.
        A 4.9 with 5 reviews is less trustworthy than 4.7 with 5000 reviews.
        
        Bayesian approximation bonus:
        - < 100 reviews:   +0 points
        - 100-999 reviews: +5 points
        - 1000+ reviews:   +10 points
        
        Args:
            user_ratings_total: Number of Google reviews
        
        Returns:
            Bonus points (0, 5, or 10)
        """
        if user_ratings_total is None:
            return 0.0
        
        if user_ratings_total >= 1000:
            # Highly reviewed - very trustworthy
            return 10.0
        elif user_ratings_total >= 100:
            # Moderately reviewed - somewhat trustworthy
            return 5.0
        else:
            # Few reviews - no bonus
            return 0.0
    
    def calculate_score(
        self,
        place: CandidatePlace,
        weather: Optional[Dict[str, Any]],
        centroid_lat: float,
        centroid_lng: float
    ) -> float:
        """
        Calculate the final utility score for a single place.
        
        Formula:
        score = (base_score * distance_mult * weather_mult) + social_bonus
        
        Where:
        - base_score = rating * 20 (0-100)
        - distance_mult = e^(-0.15 * km) (0-1)
        - weather_mult = 0.3 to 1.0 based on conditions
        - social_bonus = 0, 5, or 10 based on review count
        
        Args:
            place: CandidatePlace object
            weather: Weather data dict
            centroid_lat, centroid_lng: Trip centroid coordinates
        
        Returns:
            Final utility score (0.0 to ~110.0)
        """
        # 1. Base Score from rating
        base_score = self.calculate_base_score(place.rating)
        
        # 2. Gravity Factor (distance decay)
        distance_mult = self.calculate_distance_multiplier(
            place.lat, place.lng,
            centroid_lat, centroid_lng
        )
        
        # 3. Reality Factor (weather penalty)
        weather_mult = self.calculate_weather_multiplier(
            place.types, place.category, weather
        )
        
        # 4. Social Proof Boost
        social_bonus = self.calculate_social_proof_bonus(place.user_ratings_total)
        
        # Final score calculation
        # Multiplicative factors apply to base, then add bonus
        final_score = (base_score * distance_mult * weather_mult) + social_bonus
        
        return final_score
    
    def rank_places(
        self,
        places: List[Dict[str, Any]],
        weather: Optional[Dict[str, Any]] = None,
        centroid: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank and filter places by utility score.
        
        Process:
        1. Convert dicts to CandidatePlace objects
        2. Calculate centroid if not provided (average of all coordinates)
        3. Score each place
        4. Filter out places with score < 40.0
        5. Sort by score descending
        6. Return as list of dicts
        
        Args:
            places: List of place dictionaries from Google Places API
            weather: Optional weather data {'main': str, 'temp': float}
            centroid: Optional centroid {'lat': float, 'lng': float}
        
        Returns:
            Filtered and sorted list of place dicts with 'score' field added
        """
        if not places:
            return []
        
        # Convert to CandidatePlace objects
        candidates = [CandidatePlace.from_dict(p) for p in places]
        
        # Calculate centroid if not provided (average of all valid coordinates)
        if centroid is None:
            valid_coords = [
                (c.lat, c.lng) for c in candidates 
                if c.lat is not None and c.lng is not None
            ]
            if valid_coords:
                centroid_lat = sum(lat for lat, _ in valid_coords) / len(valid_coords)
                centroid_lng = sum(lng for _, lng in valid_coords) / len(valid_coords)
            else:
                # Fallback to first place with coords or 0,0
                centroid_lat, centroid_lng = 0.0, 0.0
        else:
            centroid_lat = centroid.get("lat", 0.0)
            centroid_lng = centroid.get("lng", 0.0)
        
        # Calculate scores for all candidates
        for candidate in candidates:
            candidate.score = self.calculate_score(
                candidate, weather, centroid_lat, centroid_lng
            )
        
        # Filter out low-scoring places
        qualified = [c for c in candidates if c.score >= self.MIN_SCORE_THRESHOLD]
        
        # Sort by score descending
        qualified.sort(key=lambda c: c.score, reverse=True)
        
        # Convert back to dicts
        return [c.to_dict() for c in qualified]


def rank_places(
    places: List[Dict[str, Any]],
    weather: Optional[Dict[str, Any]] = None,
    centroid: Optional[Dict[str, float]] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function to rank places without instantiating UtilityScorer.
    
    Args:
        places: List of place dictionaries
        weather: Optional weather data {'main': str, 'temp': float}
        centroid: Optional centroid {'lat': float, 'lng': float}
    
    Returns:
        Filtered and sorted list of place dicts with scores
    """
    scorer = UtilityScorer()
    return scorer.rank_places(places, weather, centroid)


# For testing
if __name__ == "__main__":
    import json
    
    # Sample places (simulating Google Places data)
    test_places = [
        {
            "name": "Vancouver Aquarium",
            "lat": 49.3004876,
            "lng": -123.1308774,
            "types": ["aquarium", "tourist_attraction"],
            "rating": 4.5,
            "user_ratings_total": 15000,
            "category": "landmark",
            "why": "World-class marine life exhibits."
        },
        {
            "name": "Stanley Park",
            "lat": 49.3017,
            "lng": -123.1417,
            "types": ["park", "tourist_attraction"],
            "rating": 4.8,
            "user_ratings_total": 50000,
            "category": "nature",
            "why": "Beautiful urban park with ocean views."
        },
        {
            "name": "Random Far Away Place",
            "lat": 49.5,  # ~25km away
            "lng": -123.5,
            "types": ["restaurant"],
            "rating": 4.9,
            "user_ratings_total": 50,
            "category": "restaurant",
            "why": "Great food but very far."
        },
        {
            "name": "Low Rated Spot",
            "lat": 49.3,
            "lng": -123.13,
            "types": ["cafe"],
            "rating": 2.5,
            "user_ratings_total": 200,
            "category": "restaurant",
            "why": "Mediocre cafe."
        },
    ]
    
    # Test 1: Good weather
    print("=== Test 1: Good Weather ===")
    weather_good = {"main": "Clear", "temp": 20.0}
    results = rank_places(test_places, weather_good)
    print(json.dumps(results, indent=2))
    
    # Test 2: Rainy weather (should penalize Stanley Park)
    print("\n=== Test 2: Rainy Weather ===")
    weather_rain = {"main": "Rain", "temp": 10.0}
    results = rank_places(test_places, weather_rain)
    print(json.dumps(results, indent=2))
