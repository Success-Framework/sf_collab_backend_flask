import os
from flask import current_app
from groq import Groq
from openai import OpenAI


def generate_subtitles(prompt, video_duration):
    """
    Generate basic SRT subtitles using AI.
    """

    text = _generate_subtitle_text(prompt)

    srt_path = os.path.join(
        os.getcwd(),
        "uploads",
        "video_temp",
        "subtitles.srt"
    )

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(text)

    return srt_path


def _generate_subtitle_text(prompt):
    groq_key = current_app.config.get("GROQ_API_KEY")

    if groq_key:
        client = Groq(api_key=groq_key)
        response = client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=[
                {
                    "role": "system",
                    "content": "Generate SRT subtitles for a video edit request."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=500
        )
        return response.choices[0].message.content

    # fallback
    return """1
00:00:00,000 --> 00:00:05,000
Subtitle generation failed
"""
