from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
from dotenv import load_dotenv

from agents import generate_candidates
from places_api import enrich_candidates_sync, get_photo_url

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="go. API", version="0.1.0")

# CORS Configuration - Allow all for hackathon speed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class TravelPrompt(BaseModel):
    prompt: str

class TripRequest(BaseModel):
    city: str
    start_date: str
    end_date: str
    vibe: Optional[str] = ""

class Place(BaseModel):
    name: str
    search_query: str
    category: str
    why: str
    place_id: Optional[str] = None
    formatted_address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    opening_hours: Optional[bool] = None
    price_level: Optional[int] = None
    photo_url: Optional[str] = None

class TripResponse(BaseModel):
    status: str
    city: str
    start_date: str
    end_date: str
    vibe: Optional[str]
    places: List[Place]

# Root endpoint
@app.get("/")
async def root():
    return {"status": "go. online"}

# Generate trip endpoint - THE MAIN ENDPOINT
@app.post("/generate", response_model=TripResponse)
async def generate_trip(request: TripRequest):
    """
    Generate travel recommendations for a city.
    1. Claude generates candidate places
    2. Google Places enriches with real coordinates
    """
    
    # Calculate trip duration and number of places
    try:
        start = datetime.strptime(request.start_date, "%Y-%m-%d")
        end = datetime.strptime(request.end_date, "%Y-%m-%d")
        num_days = max(1, (end - start).days + 1)  # At least 1 day
    except ValueError:
        num_days = 3  # Default fallback
    
    # Scale places based on trip length: ~3-4 places per day, min 5, max 15
    num_places = min(15, max(5, num_days * 3))
    
    # Step 1: Get candidates from Claude
    candidates = generate_candidates(
        city=request.city,
        vibe=request.vibe or "",
        num_places=num_places
    )
    
    if not candidates:
        return {
            "status": "error",
            "city": request.city,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "vibe": request.vibe,
            "places": []
        }
    
    # Step 2: Enrich with Google Places data (parallel fetching)
    enriched_places = enrich_candidates_sync(candidates)
    
    # Step 3: Add photo URLs
    for place in enriched_places:
        if place.get("photo_reference"):
            place["photo_url"] = get_photo_url(place["photo_reference"])
        else:
            place["photo_url"] = None
    
    return {
        "status": "success",
        "city": request.city,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "vibe": request.vibe,
        "places": enriched_places
    }

# Legacy endpoint for backwards compatibility
@app.post("/generate-legacy")
async def generate_itinerary(request: TravelPrompt):
    """
    Legacy endpoint - kept for backwards compatibility.
    """
    
    dummy_itinerary = {
        "destination": "Extracted from prompt: " + request.prompt,
        "days": 3,
        "activities": [
            {
                "day": 1,
                "title": "Arrival & Exploration",
                "description": "Check in and explore the local area",
                "time": "All day"
            }
        ]
    }
    
    return {
        "status": "success",
        "itinerary": dummy_itinerary
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "go. backend"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
