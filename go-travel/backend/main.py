from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
from dotenv import load_dotenv

from agents import generate_candidates
from places_api import enrich_candidates, get_photo_url
from scoring import rank_places
from weather import fetch_weather
from solver import solve_itinerary
from response_models import format_itinerary_response, format_error_response

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="go. API", version="0.2.0")

# CORS Configuration - Allow all for hackathon speed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class TripRequest(BaseModel):
    city: str
    start_date: str
    end_date: str
    vibe: Optional[str] = ""

# Root endpoint
@app.get("/")
async def root():
    return {"status": "go. online", "version": "0.2.0"}

# Generate trip endpoint - THE MAIN ENDPOINT
@app.post("/generate")
async def generate_trip(request: TripRequest):
    """
    Generate a full multi-day itinerary for a city.
    
    Pipeline:
    1. Claude generates candidate places (agents.py)
    2. Google Places enriches with real coordinates (places_api.py)
    3. Weather API fetches current conditions (weather.py)
    4. Scoring ranks places by utility (scoring.py)
    5. OR-Tools solver optimizes multi-day routes (solver.py)
    6. Response formatter structures output (response_models.py)
    """
    
    try:
        # Calculate trip duration
        try:
            start = datetime.strptime(request.start_date, "%Y-%m-%d")
            end = datetime.strptime(request.end_date, "%Y-%m-%d")
            num_days = max(1, (end - start).days + 1)
        except ValueError:
            num_days = 3  # Default fallback
        
        # Scale places based on trip length: 6 places per day, min 6, max 30
        num_places = min(30, max(6, num_days * 6))
        
        print(f"[go.] Generating {num_places} places for {num_days}-day trip to {request.city}")
        
        # ===== STEP 1: Generate candidates with Claude =====
        print("[go.] Step 1: Generating candidates with Claude...")
        candidates = generate_candidates(
            city=request.city,
            vibe=request.vibe or "",
            num_places=num_places
        )
        
        if not candidates:
            return format_error_response(
                error_message="Failed to generate place recommendations. Please try again.",
                city=request.city,
                vibe=request.vibe or ""
            )
        
        print(f"[go.] Generated {len(candidates)} candidates")
        
        # ===== STEP 2: Enrich with Google Places =====
        print("[go.] Step 2: Enriching with Google Places API...")
        enriched_places = await enrich_candidates(candidates)
        
        # Add photo URLs
        for place in enriched_places:
            if place.get("photo_reference"):
                place["photo_url"] = get_photo_url(place["photo_reference"])
        
        print(f"[go.] Enriched {len(enriched_places)} places with coordinates")
        
        # ===== STEP 3: Fetch weather =====
        print("[go.] Step 3: Fetching weather data...")
        weather = await fetch_weather(request.city)
        if weather:
            print(f"[go.] Weather: {weather.get('temp', '?')}°C, {weather.get('description', 'unknown')}")
        
        # ===== STEP 4: Score and rank places =====
        print("[go.] Step 4: Scoring and ranking places...")
        scored_places = rank_places(enriched_places, weather=weather)
        print(f"[go.] {len(scored_places)} places passed scoring threshold")
        
        if not scored_places:
            return format_error_response(
                error_message="No places met the quality threshold. Try a different vibe.",
                city=request.city,
                vibe=request.vibe or ""
            )
        
        # ===== STEP 5: Solve multi-day itinerary =====
        print("[go.] Step 5: Optimizing multi-day itinerary with OR-Tools...")
        
        # Calculate hotel coords (centroid of places)
        valid_coords = [(p["lat"], p["lng"]) for p in scored_places if p.get("lat") and p.get("lng")]
        if valid_coords:
            hotel_lat = sum(c[0] for c in valid_coords) / len(valid_coords)
            hotel_lng = sum(c[1] for c in valid_coords) / len(valid_coords)
            hotel_coords = (hotel_lat, hotel_lng)
        else:
            hotel_coords = None
        
        solver_output = solve_itinerary(
            places=scored_places,
            hotel_coords=hotel_coords,
            num_days=num_days,
            time_limit_seconds=10
        )
        
        total_places = sum(d["num_places"] for d in solver_output)
        print(f"[go.] Solver assigned {total_places} places across {num_days} days")
        
        # ===== STEP 6: Format response =====
        print("[go.] Step 6: Formatting response...")
        response = format_itinerary_response(
            city=request.city,
            vibe=request.vibe or "",
            num_days=num_days,
            start_date=request.start_date,
            solver_output=solver_output,
            original_places=scored_places,
            hotel_coords=hotel_coords,
            weather=weather,
        )
        
        print(f"[go.] ✓ Itinerary complete!")
        return response
        
    except Exception as e:
        print(f"[go.] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return format_error_response(
            error_message=f"An error occurred: {str(e)}",
            city=request.city,
            vibe=request.vibe or ""
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "go. backend",
        "version": "0.2.0"
    }

if __name__ == "__main__":
    import uvicorn
    print("[go.] Starting server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
