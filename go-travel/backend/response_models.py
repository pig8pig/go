"""
Response Models - Standardized API Response Formats
====================================================
Defines the exact JSON structure that the frontend expects.
All itinerary endpoints MUST return data in these formats.

Author: go. travel planner
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum


class PlaceCategory(str, Enum):
    """Supported place categories."""
    LANDMARK = "landmark"
    MUSEUM = "museum"
    RESTAURANT = "restaurant"
    NATURE = "nature"
    NIGHTLIFE = "nightlife"
    SHOPPING = "shopping"
    CULTURAL = "cultural"
    CAFE = "cafe"
    OTHER = "other"


class Coordinates(BaseModel):
    """Geographic coordinates."""
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")


class TimeSlot(BaseModel):
    """Time information for an itinerary item."""
    arrival: str = Field(..., description="Arrival time (e.g., '9:30 AM')")
    departure: str = Field(..., description="Departure time (e.g., '11:00 AM')")
    duration_minutes: int = Field(..., description="Visit duration in minutes")


class ItineraryPlace(BaseModel):
    """
    A single place in the itinerary.
    This is what the frontend displays for each stop.
    """
    id: str = Field(..., description="Unique place identifier")
    name: str = Field(..., description="Place name")
    category: str = Field(..., description="Place category (landmark, museum, etc.)")
    coordinates: Coordinates
    time: TimeSlot
    score: float = Field(..., description="Utility score (0-100)")
    why: str = Field(..., description="Why this place was recommended")
    address: Optional[str] = Field(None, description="Formatted address")
    photo_url: Optional[str] = Field(None, description="Photo URL if available")
    rating: Optional[float] = Field(None, description="Google rating (1-5)")
    review_count: Optional[int] = Field(None, description="Number of reviews")


class DayPlan(BaseModel):
    """
    One day's complete itinerary.
    """
    day_number: int = Field(..., description="Day number (1-indexed)")
    date: Optional[str] = Field(None, description="Actual date if provided (YYYY-MM-DD)")
    places: List[ItineraryPlace] = Field(default_factory=list)
    summary: "DaySummary"


class DaySummary(BaseModel):
    """Summary statistics for a single day."""
    num_places: int = Field(..., description="Number of places to visit")
    total_score: float = Field(..., description="Sum of all place scores")
    travel_time_minutes: int = Field(..., description="Total travel time")
    visit_time_minutes: int = Field(..., description="Total time at places")
    total_time_minutes: int = Field(..., description="Travel + visit time")
    start_time: Optional[str] = Field(None, description="First activity start time")
    end_time: Optional[str] = Field(None, description="Last activity end time")


class TripSummary(BaseModel):
    """Overall trip statistics."""
    city: str = Field(..., description="Destination city")
    num_days: int = Field(..., description="Number of days")
    start_date: Optional[str] = Field(None, description="Trip start date")
    end_date: Optional[str] = Field(None, description="Trip end date")
    total_places: int = Field(..., description="Total places in itinerary")
    total_score: float = Field(..., description="Sum of all scores")
    places_dropped: int = Field(0, description="Places that didn't fit")
    vibe: Optional[str] = Field(None, description="Trip vibe/theme")


class ItineraryResponse(BaseModel):
    """
    THE MAIN RESPONSE FORMAT.
    This is what /generate returns to the frontend.
    
    Example:
    {
        "success": true,
        "trip": {
            "city": "Tokyo",
            "num_days": 3,
            "start_date": "2026-02-15",
            "end_date": "2026-02-17",
            "total_places": 12,
            "total_score": 892.5,
            "places_dropped": 2,
            "vibe": "adventure"
        },
        "days": [
            {
                "day_number": 1,
                "date": "2026-02-15",
                "places": [...],
                "summary": {...}
            },
            ...
        ],
        "hotel": {
            "lat": 35.6812,
            "lng": 139.7671
        }
    }
    """
    success: bool = Field(True, description="Whether generation succeeded")
    error: Optional[str] = Field(None, description="Error message if failed")
    trip: TripSummary
    days: List[DayPlan]
    hotel: Optional[Coordinates] = Field(None, description="Hotel/starting point")


# Update forward reference
DayPlan.model_rebuild()


def format_itinerary_response(
    city: str,
    vibe: str,
    num_days: int,
    start_date: Optional[str],
    solver_output: List[Dict[str, Any]],
    original_places: List[Dict[str, Any]],
    hotel_coords: Optional[tuple] = None,
) -> Dict[str, Any]:
    """
    Convert solver output to the standardized ItineraryResponse format.
    
    Args:
        city: Destination city
        vibe: Trip vibe/theme
        num_days: Number of days
        start_date: Trip start date (YYYY-MM-DD) or None
        solver_output: Raw output from solve_itinerary()
        original_places: All candidate places (to calculate dropped)
        hotel_coords: (lat, lng) tuple
    
    Returns:
        Dict matching ItineraryResponse schema
    """
    # Calculate totals
    total_places = sum(day["num_places"] for day in solver_output)
    total_score = sum(day["total_score"] for day in solver_output)
    places_dropped = len(original_places) - total_places
    
    # Calculate end date if start date provided
    end_date = None
    if start_date and num_days > 1:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = start + timedelta(days=num_days - 1)
            end_date = end.strftime("%Y-%m-%d")
        except:
            end_date = None
    elif start_date:
        end_date = start_date
    
    # Build trip summary
    trip = {
        "city": city,
        "num_days": num_days,
        "start_date": start_date,
        "end_date": end_date,
        "total_places": total_places,
        "total_score": round(total_score, 1),
        "places_dropped": places_dropped,
        "vibe": vibe,
    }
    
    # Build days
    days = []
    for day_data in solver_output:
        day_num = day_data["day"]
        
        # Calculate day's date
        day_date = None
        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                day_dt = start + timedelta(days=day_num - 1)
                day_date = day_dt.strftime("%Y-%m-%d")
            except:
                day_date = None
        
        # Convert places to ItineraryPlace format
        places = []
        for item in day_data["items"]:
            place = {
                "id": item.get("place_id", ""),
                "name": item.get("name", ""),
                "category": item.get("category", "other"),
                "coordinates": {
                    "lat": item.get("lat", 0),
                    "lng": item.get("lng", 0),
                },
                "time": {
                    "arrival": item.get("arrival_time_formatted", ""),
                    "departure": item.get("departure_time_formatted", ""),
                    "duration_minutes": item.get("duration", 60),
                },
                "score": round(item.get("score", 0), 1),
                "why": item.get("why", ""),
                "address": item.get("formatted_address"),
                "photo_url": item.get("photo_url"),
                "rating": item.get("rating"),
                "review_count": item.get("review_count"),
            }
            places.append(place)
        
        # Build day summary
        summary = {
            "num_places": day_data["num_places"],
            "total_score": round(day_data["total_score"], 1),
            "travel_time_minutes": day_data["total_travel_time"],
            "visit_time_minutes": day_data["total_visit_time"],
            "total_time_minutes": day_data["total_time"],
            "start_time": places[0]["time"]["arrival"] if places else None,
            "end_time": places[-1]["time"]["departure"] if places else None,
        }
        
        days.append({
            "day_number": day_num,
            "date": day_date,
            "places": places,
            "summary": summary,
        })
    
    # Build hotel
    hotel = None
    if hotel_coords:
        hotel = {"lat": hotel_coords[0], "lng": hotel_coords[1]}
    
    return {
        "success": True,
        "error": None,
        "trip": trip,
        "days": days,
        "hotel": hotel,
    }


def format_error_response(error_message: str, city: str = "", vibe: str = "") -> Dict[str, Any]:
    """
    Create an error response in the standard format.
    """
    return {
        "success": False,
        "error": error_message,
        "trip": {
            "city": city,
            "num_days": 0,
            "start_date": None,
            "end_date": None,
            "total_places": 0,
            "total_score": 0,
            "places_dropped": 0,
            "vibe": vibe,
        },
        "days": [],
        "hotel": None,
    }


# Example response for frontend reference
EXAMPLE_RESPONSE = {
    "success": True,
    "error": None,
    "trip": {
        "city": "Tokyo",
        "num_days": 3,
        "start_date": "2026-02-15",
        "end_date": "2026-02-17",
        "total_places": 10,
        "total_score": 823.5,
        "places_dropped": 2,
        "vibe": "adventure"
    },
    "days": [
        {
            "day_number": 1,
            "date": "2026-02-15",
            "places": [
                {
                    "id": "ChIJ51cu8IcbXWARiRtXIothAS4",
                    "name": "Senso-ji Temple",
                    "category": "landmark",
                    "coordinates": {"lat": 35.7148, "lng": 139.7967},
                    "time": {
                        "arrival": "9:30 AM",
                        "departure": "10:15 AM",
                        "duration_minutes": 45
                    },
                    "score": 95.0,
                    "why": "Tokyo's oldest temple with stunning architecture",
                    "address": "2-3-1 Asakusa, Taito City, Tokyo",
                    "photo_url": "https://places.googleapis.com/...",
                    "rating": 4.6,
                    "review_count": 52341
                }
            ],
            "summary": {
                "num_places": 4,
                "total_score": 312.5,
                "travel_time_minutes": 45,
                "visit_time_minutes": 240,
                "total_time_minutes": 285,
                "start_time": "9:30 AM",
                "end_time": "5:15 PM"
            }
        }
    ],
    "hotel": {"lat": 35.6812, "lng": 139.7671}
}


if __name__ == "__main__":
    import json
    print("EXAMPLE ITINERARY RESPONSE FORMAT:")
    print("="*60)
    print(json.dumps(EXAMPLE_RESPONSE, indent=2))
