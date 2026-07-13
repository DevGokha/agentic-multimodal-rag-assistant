import logging
import urllib.parse
from typing import Any

logger = logging.getLogger("image_gen")

def enhance_prompt(query: str, llm: Any) -> str:
    """Uses the LLM to extract and enhance the image prompt from the user's query."""
    prompt = f"""You are an expert AI image prompt engineer.
The user wants to generate an image. Extract what they want to see, and enhance it into a highly detailed, photorealistic prompt.
You MUST include strong quality modifiers at the end (e.g., "masterpiece, 8k resolution, highly detailed, photorealistic, cinematic lighting").
Keep the prompt concise but extremely descriptive.
DO NOT include any conversational text like "Here is the prompt" or "I will generate".
Just output the raw prompt string.

User Query: {query}
"""
    try:
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        # Clean up any surrounding quotes or backticks the LLM might add
        clean_prompt = content.strip('`"\'\n ')
        return clean_prompt
    except Exception as e:
        logger.error(f"Error enhancing image prompt: {e}")
        # Fallback to the raw query if LLM fails
        return query.strip()

def get_image_url(prompt: str) -> str:
    """URL-encodes the prompt and returns the Pollinations API image URL using the high-quality Flux model."""
    encoded_prompt = urllib.parse.quote(prompt)
    # Appending &model=flux to use the state-of-the-art Flux model which produces much better anatomy and photorealism
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&model=flux"
