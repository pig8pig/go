from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import os
from dotenv import load_dotenv

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

class ItineraryResponse(BaseModel):
    status: str
    itinerary: Dict[str, Any]

# Root endpoint
@app.get("/")
async def root():
    return {"status": "go. online"}

# Generate itinerary endpoint
@app.post("/generate", response_model=ItineraryResponse)
async def generate_itinerary(request: TravelPrompt):
    """
    Generate a travel itinerary based on user prompt.
    Currently returns a dummy itinerary - connect to AI service later.
    """
    
    # Dummy itinerary response
    dummy_itinerary = {
        "destination": "Extracted from prompt: " + request.prompt,
        "days": 3,
        "activities": [
            {
                "day": 1,
                "title": "Arrival & Exploration",
                "description": "Check in and explore the local area",
                "time": "All day"
            },
            {
                "day": 2,
                "title": "Main Attractions",
                "description": "Visit key landmarks and attractions",
                "time": "9:00 AM - 6:00 PM"
            },
            {
                "day": 3,
                "title": "Departure",
                "description": "Last minute shopping and departure",
                "time": "Morning"
            }
        ],
        "budget_estimate": "$$",
        "tips": [
            "Pack light",
            "Book tickets in advance",
            "Try local cuisine"
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
