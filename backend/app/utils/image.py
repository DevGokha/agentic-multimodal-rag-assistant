import os
import base64
import requests

# Step 1: Check if Groq API key is available (for cloud deployment)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Step 2: Ollama config for local development
VISION_MODEL = "moondream"
OLLAMA_BASE = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_API = f"{OLLAMA_BASE}/api/generate"

# Step 3: Groq config for cloud deployment
GROQ_API = "https://api.groq.com/openai/v1/chat/completions"
GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


def analyze_image(image_path: str, query: str = "Describe this image in detail."):
    """
    Step 4: Analyze an image using either Groq (cloud) or Ollama (local).
    - If GROQ_API_KEY is set → uses Groq's vision model (no GPU needed)
    - Otherwise → uses Ollama's moondream model (local GPU)
    """

    # Step 5: Read the image file and encode it as base64
    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    if GROQ_API_KEY:
        # Step 6a: Use Groq vision API (cloud deployment)
        response = requests.post(
            GROQ_API,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_VISION_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": query},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                },
                            },
                        ],
                    }
                ],
                "max_tokens": 256,
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    else:
        # Step 6b: Use Ollama vision API (local development)
        response = requests.post(
            OLLAMA_API,
            json={
                "model": VISION_MODEL,
                "prompt": query,
                "images": [image_base64],
                "stream": False,
                "options": {"num_predict": 256},
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["response"]
