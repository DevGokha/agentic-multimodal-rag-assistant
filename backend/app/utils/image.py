import base64
import requests

# Step 1: Define the vision model to use for image understanding
# "moondream" is lightweight (~1.7GB) and works well on limited GPU
# You can switch to "llava" for better quality if your GPU has enough memory
VISION_MODEL = "moondream"

# Step 2: Ollama API endpoint for generating responses
OLLAMA_API = "http://localhost:11434/api/generate"


def analyze_image(image_path: str, query: str = "Describe this image in detail."):
    """
    Step 3: Send an image to the Ollama vision model and get a text description.
    - Reads the image file from disk
    - Converts it to base64 (required by Ollama's API)
    - Sends it along with a prompt to the vision model
    - Returns the model's text description of the image
    """

    # Step 4: Read the image file and encode it as base64
    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    # Step 5: Call Ollama's API with the vision model, prompt, and image
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

    # Step 6: Raise an error if the API call failed
    response.raise_for_status()

    # Step 7: Extract and return the text response from the model
    return response.json()["response"]
