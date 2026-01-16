import requests
import base64
from flask import current_app

HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

DEFAULT_PROMPT_TEMPLATE = """
You are a professional image generation system.

Generate a high-quality, realistic, well-composed image.
Avoid distortions, extra limbs, blur, text artifacts, watermarks, logos, or noise.
No NSFW, sexual, violent, political, or hateful content.
Centered composition, clean background, professional lighting.

User request:
"{prompt}"
"""

def generate_image(prompt: str) -> str:
    api_key = current_app.config.get("HUGGINGFACE_API_KEY")
    if not api_key:
        raise RuntimeError("Hugging Face API key not configured")

    final_prompt = DEFAULT_PROMPT_TEMPLATE.format(prompt=prompt)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": final_prompt
    }

    response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)

    if response.status_code != 200:
        raise RuntimeError(f"HuggingFace error: {response.text}")

    # HuggingFace returns raw image bytes
    image_bytes = response.content
    return base64.b64encode(image_bytes).decode("utf-8")
