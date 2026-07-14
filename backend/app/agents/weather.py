import httpx
import logging
from typing import Any

logger = logging.getLogger("weather")

def extract_city(query: str, llm: Any) -> str:
    """Uses the LLM to extract the city name from the user's query."""
    prompt = f"""Extract the city name from the following weather query. 
Return ONLY the city name, nothing else. If you cannot find a city, return 'Unknown'.
Query: {query}
City:"""
    try:
        response = llm.invoke(prompt)
        # Handle both AIMessage and string responses depending on LangChain version
        content = response.content if hasattr(response, "content") else str(response)
        city = content.strip()
        
        if "Unknown" in city or not city:
            return ""
        return city
    except Exception as e:
        logger.error(f"Error extracting city: {e}")
        return ""

def fetch_weather(city: str) -> str:
    """Fetches weather data from Open-Meteo or wttr.in for the given city."""
    if not city:
        return "No city provided for weather search."
    
    try:
        # Step 1: Geocoding (Convert city name to lat/lon)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = httpx.get(geo_url, timeout=15.0)
        geo_data = geo_res.json()
        
        if not geo_data.get("results"):
            raise ValueError("No geocoding results.")
            
        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        full_name = f"{location.get('name', city)}, {location.get('country', '')}".strip(", ")
        
        # Step 2: Forecast (Get current weather)
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_res = httpx.get(weather_url, timeout=15.0)
        w_data = w_res.json()
        
        if "current_weather" not in w_data:
            raise ValueError("No current weather data in response.")
            
        cw = w_data["current_weather"]
        temp = cw.get("temperature")
        windspeed = cw.get("windspeed")
        
        return f"The current weather in {full_name} is {temp}°C with a wind speed of {windspeed} km/h."
        
    except Exception as e:
        logger.warning(f"Open-Meteo failed for {city}: {e}. Falling back to wttr.in...")
        try:
            # Fallback to wttr.in with User-Agent to bypass bot protections
            wttr_url = f"https://wttr.in/{city}?format=j1"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            w_res = httpx.get(wttr_url, headers=headers, timeout=15.0)
            w_data = w_res.json()
            
            cw = w_data["current_condition"][0]
            temp = cw.get("temp_C")
            windspeed = cw.get("windspeedKmph")
            desc = cw.get("weatherDesc")[0].get("value", "")
            
            return f"The current weather in {city} is {temp}°C, {desc}, with a wind speed of {windspeed} km/h."
        except Exception as e2:
            logger.warning(f"wttr.in failed for {city}: {e2}. Falling back to Web Search...")
            try:
                from app.agents.web_search import web_search_tool
                search_query = f"current weather temperature in {city} right now"
                search_results = web_search_tool(search_query)
                return f"Weather Data from Web Search:\n{search_results}"
            except Exception as e3:
                logger.error(f"Error fetching weather from Web Search fallback for {city}: {e3}")
                return f"Failed to fetch weather from all sources."
