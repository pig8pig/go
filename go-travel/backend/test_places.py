"""Quick test for Google Places API"""
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def test():
    key = os.getenv('GOOGLE_PLACES_API_KEY')
    print(f"Using key: {key[:20]}...")
    
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': key,
        'X-Goog-FieldMask': 'places.displayName,places.location,places.rating,places.formattedAddress'
    }
    
    payload = {'textQuery': 'Tokyo Tower'}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://places.googleapis.com/v1/places:searchText',
            headers=headers,
            json=payload
        ) as response:
            result = await response.json()
            print(f"Status: {response.status}")
            print(f"Response: {result}")

if __name__ == "__main__":
    asyncio.run(test())
