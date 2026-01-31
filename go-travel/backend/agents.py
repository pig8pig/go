"""
Agent Layer - Claude API for generating travel candidates
"""

import anthropic
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Anthropic client
client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

def generate_candidates(city: str, vibe: str = "", num_places: int = 10) -> list[dict]:
    """
    Call Claude to generate candidate places for a city.
    Returns a list of dicts with 'name' and 'search_query' only.
    Claude does NOT provide coordinates (it hallucinates them).
    """
    
    vibe_context = f" The traveler is looking for a {vibe} vibe." if vibe else ""
    
    prompt = f"""You are a travel expert. Generate exactly {num_places} must-visit places for someone traveling to {city}.{vibe_context}

IMPORTANT: Return ONLY a valid JSON array. No markdown, no explanation, no code blocks.

Each place should have:
- "name": The official name of the place
- "search_query": A search string to find this place on Google Maps (include city name for accuracy)
- "category": One of: "landmark", "restaurant", "museum", "nature", "nightlife", "shopping", "cultural"
- "why": One sentence on why to visit (max 15 words)

Example format:
[
  {{"name": "Eiffel Tower", "search_query": "Eiffel Tower Paris France", "category": "landmark", "why": "Iconic symbol of Paris with stunning city views."}},
  {{"name": "Le Comptoir du Panthéon", "search_query": "Le Comptoir du Panthéon Paris", "category": "restaurant", "why": "Classic Parisian café with amazing croissants."}}
]

Return exactly {num_places} diverse places covering different categories. JSON only:"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the response text
        response_text = message.content[0].text.strip()
        
        # Clean up response if needed (remove markdown code blocks if present)
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        response_text = response_text.strip()
        
        # Parse JSON
        candidates = json.loads(response_text)
        
        return candidates
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw response: {response_text}")
        return []
    except Exception as e:
        print(f"Claude API error: {e}")
        return []


# For testing
if __name__ == "__main__":
    results = generate_candidates("Tokyo", "foodie")
    print(json.dumps(results, indent=2))
