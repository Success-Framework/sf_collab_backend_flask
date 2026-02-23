import requests
import base64
from flask import current_app
import concurrent.futures

MODELS = [
    "prompthero/openjourney",
    "Bingsu/my-korean-stable-diffusion-v1-5",            # i Have just added random model so pls suggest any choice u have
    "stabilityai/stable-diffusion-xl-base-1.0"
]

DEFAULT_PROMPT_TEMPLATE = """
You are a professional image generation system.
Generate a high-quality, realistic, well-composed image.
Avoid distortions, extra limbs, blur, text artifacts, watermarks, logos, or noise.
No NSFW, sexual, violent, political, or hateful content.
Centered composition, clean background, professional lighting.

User request:
"{prompt}"
"""

def fetch_single_model(model_id, prompt, api_key):
    HF_url = f"https://api-inference.huggingface.co/models/{model_id}" # For dynamic HaNdling of multiple models
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {"inputs": prompt}  

    try:
        response = requests.post(HF_url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            img_str = base64.b64encode(response.content).decode("utf-8")
            return {"model": model_id, "image": img_str, "status": "success"}
        else:
            return {"model": model_id, "error": "Model is busy", "status": "failed"}
    except Exception as e:
        return {"model": model_id, "error": str(e), "status": "failed"}


def generate_multiple_images(prompt: str):
    api_key = current_app.config.get("HF_API_KEY")
    
    final_prompt = DEFAULT_PROMPT_TEMPLATE.format(prompt=prompt)  
    
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:  # WE could increse IF we Want 
            future_tasks = [
                executor.submit(fetch_single_model, model_id, final_prompt, api_key)
                for model_id in MODELS
            ]
            for future in concurrent.futures.as_completed(future_tasks):
                results.append(future.result())

    return results