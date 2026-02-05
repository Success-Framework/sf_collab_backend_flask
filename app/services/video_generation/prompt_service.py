from flask import current_app
from groq import Groq
from openai import OpenAI
import logging


def get_groq_client():
    key = current_app.config.get("GROQ_API_KEY")
    return Groq(api_key=key) if key else None


def get_openai_client():
    key = current_app.config.get("OPENAI_API_KEY")
    return OpenAI(api_key=key) if key else None


def enhance_video_prompt(
    *,
    mode: str,
    user_prompt: str,
    duration: int,
    style: str = None
) -> str:
    """
    Enhance a user prompt for AI video generation.
    Groq-first, OpenAI-optional, safe fallback.
    """

    system_prompt = (
        "You are a professional AI video prompt engineer. "
        "Convert the user's idea into a vivid, cinematic, "
        "model-optimized prompt for AI video generation. "
        "Return ONLY the final prompt."
    )

    mode_guidance = {
        "text": "Focus on cinematic visuals, camera movement, lighting, mood, and motion.",
        "image": "Focus on smooth animation, realistic motion, and visual continuity.",
        "video": "Focus on video enhancement, editing, and style transformation."
    }

    composed_prompt = f"""
MODE: {mode}
DURATION: {duration} seconds
STYLE: {style or "cinematic"}

USER REQUEST:
{user_prompt}

GUIDANCE:
{mode_guidance.get(mode, "")}
"""

    # --- Groq first ---
    try:
        groq_client = get_groq_client()
        if groq_client:
            response = groq_client.chat.completions.create(
                model="qwen/qwen3-32b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": composed_prompt}
                ],
                temperature=0.6,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
    except Exception as e:
        logging.warning(f"[VideoPrompt] Groq failed: {e}")

    # --- OpenAI fallback (optional) ---
    try:
        openai_client = get_openai_client()
        if openai_client:
            response = openai_client.responses.create(
                model="gpt-4.1-mini",
                input=f"{system_prompt}\n{composed_prompt}"
            )
            return response.output_text.strip()
    except Exception as e:
        logging.warning(f"[VideoPrompt] OpenAI fallback failed: {e}")

    # --- Final fallback ---
    return user_prompt
