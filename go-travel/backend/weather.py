"""
Weather Module - OpenWeatherMap API Integration
================================================
Fetches current weather data for scoring outdoor activities.
"""

import aiohttp
import asyncio
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"


async def fetch_weather(city: str) -> Optional[Dict[str, Any]]:
    """
    Fetch current weather for a city from OpenWeatherMap.
    
    Args:
        city: City name (e.g., "Vancouver", "Tokyo, JP")
    
    Returns:
        Dict with 'main' (condition), 'temp' (celsius), 'description'
        or None if API fails
    """
    if not OPENWEATHER_API_KEY:
        print("WARNING: OPENWEATHER_API_KEY not set")
        return None
    
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"  # Celsius
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(WEATHER_API_URL, params=params) as response:
                if response.status != 200:
                    print(f"Weather API error: {response.status}")
                    return None
                
                data = await response.json()
                
                # Extract relevant weather info
                weather = {
                    "main": data.get("weather", [{}])[0].get("main", "Unknown"),
                    "description": data.get("weather", [{}])[0].get("description", ""),
                    "temp": data.get("main", {}).get("temp", 20.0),
                    "feels_like": data.get("main", {}).get("feels_like", 20.0),
                    "humidity": data.get("main", {}).get("humidity", 50),
                    "city": data.get("name", city),
                    "country": data.get("sys", {}).get("country", "")
                }
                
                return weather
                
    except Exception as e:
        print(f"Weather fetch error: {e}")
        return None


def fetch_weather_sync(city: str) -> Optional[Dict[str, Any]]:
    """Synchronous wrapper for fetch_weather."""
    return asyncio.run(fetch_weather(city))


# For testing
if __name__ == "__main__":
    import json
    
    test_cities = ["Vancouver", "Tokyo", "Paris"]
    
    for city in test_cities:
        print(f"\n=== Weather for {city} ===")
        weather = fetch_weather_sync(city)
        if weather:
            print(json.dumps(weather, indent=2))
        else:
            print("Failed to fetch weather")
