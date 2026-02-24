# app/services/pitch_deck/generator.py

import json
import uuid
import re
from datetime import datetime
from flask import current_app
from groq import Groq

from app.services.pitch_deck.templates import get_template


class PitchDeckGenerator:

    def __init__(self, model="qwen/qwen3-32b"):
        self.model = model
        self.api_key = current_app.config.get("GROQ_API_KEY") # (.env → app.config → current_app.config → service)

        if not self.api_key:
            raise ValueError("Groq API key not configured")

        self.client = Groq(api_key=self.api_key)

    # ---------------------------------------------------

    def generate_deck(self, title, template_type, startup_data):

        slide_structure = get_template(template_type)

        prompt = self._build_prompt(title, slide_structure, startup_data)

        ai_response = self._call_groq(prompt)

        deck_json = self._extract_json(ai_response)

        validated_deck = self._validate_structure(deck_json, slide_structure, title)

        return validated_deck

    # ---------------------------------------------------

    def _build_prompt(self, title, slide_structure, startup_data):

        system_instruction = """
You are a world-class venture capital pitch deck expert.

IMPORTANT RULES:
- Return ONLY valid JSON.
- Do NOT include markdown.
- Do NOT include explanations.
- Do NOT wrap response in code blocks.

JSON structure MUST be:

{
  "deck_title": "",
  "slides": [
    {
      "id": "uuid",
      "type": "slide_type",
      "title": "",
      "subtitle": "",
      "bullets": [],
      "highlight": "",
      "layout": "title_bullets"
    }
  ]
}
"""

        slide_types_text = ", ".join(slide_structure)

        user_prompt = f"""
Generate an investor-ready pitch deck titled "{title}".

Slide types MUST strictly follow this order:
{slide_types_text}

Startup Information:
{json.dumps(startup_data, indent=2)}

Guidelines:
- 3–5 strong bullet points per slide
- Quantifiable metrics where possible
- Professional investor tone
- Financial slide must include 3-year projection summary
- Fundraising slide must include amount, use of funds, runway

Generate all slides strictly in given order.
"""

        return system_instruction, user_prompt

    # ---------------------------------------------------

    def _call_groq(self, prompt_tuple):

        system_prompt, user_prompt = prompt_tuple

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4096
        )

        return completion.choices[0].message.content

    # ---------------------------------------------------

    def _extract_json(self, text):

        cleaned = re.sub(r"^```(?:json)?|```$", "", text, flags=re.IGNORECASE).strip()

        match = re.search(r"\{.*\}", cleaned, re.DOTALL)

        if not match:
            raise ValueError("AI did not return valid JSON")

        return json.loads(match.group(0))

    # ---------------------------------------------------

    def _validate_structure(self, deck_json, expected_structure, title):

        if "slides" not in deck_json:
            raise ValueError("Invalid deck structure")

        slides = deck_json["slides"]

        if len(slides) != len(expected_structure):
            raise ValueError("Slide count mismatch from template")

        validated_slides = []

        for index, slide_type in enumerate(expected_structure):

            slide = slides[index]

            validated_slide = {
                "id": str(uuid.uuid4()),
                "type": slide_type,
                "title": slide.get("title", slide_type.replace("_", " ").title()),
                "subtitle": slide.get("subtitle", ""),
                "bullets": slide.get("bullets", []),
                "highlight": slide.get("highlight", ""),
                "layout": "title_bullets"
            }

            validated_slides.append(validated_slide)

        return {
            "deck_title": title,
            "generated_at": datetime.utcnow().isoformat(),
            "slides": validated_slides
        }
