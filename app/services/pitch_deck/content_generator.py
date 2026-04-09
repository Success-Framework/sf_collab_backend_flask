"""
content_generator.py
Sends founder's raw form data to AIService and returns structured
slide content as a Python dict.
"""

import json
import logging
import re
from app.services.ai_core.ai_service import AIService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def _build_prompt(form_data: dict) -> str:
    """
    Build the prompt sent to AIService.
    We ask for a strict JSON response — no markdown, no preamble.
    """

    company_name     = form_data.get("company_name", "")
    tagline          = form_data.get("tagline", "")
    founder_name     = form_data.get("founder_name", "")
    problem          = form_data.get("problem", "")
    solution         = form_data.get("solution", "")
    market_size      = form_data.get("market_size", "")
    product_desc     = form_data.get("product_description", "")
    key_features     = form_data.get("key_features", [])
    traction         = form_data.get("traction", "")
    team_members     = form_data.get("team_members", [])
    funding_ask      = form_data.get("funding_ask", "")
    use_of_funds     = form_data.get("use_of_funds", "")
    template         = form_data.get("template", "general")

    features_text = "\n".join(f"- {f}" for f in key_features if f)
    team_text     = "\n".join(
        f"- {m.get('name', '')} ({m.get('role', '')})"
        for m in team_members if m.get("name")
    )

    prompt = f"""
You are an expert startup pitch deck writer helping a founder create an investor-ready presentation.

Template style: {template.upper()}
Company: {company_name}
Tagline: {tagline}
Founder: {founder_name}

FOUNDER'S RAW INPUTS:
Problem: {problem}
Solution: {solution}
Market Size: {market_size}
Product: {product_desc}
Key Features:
{features_text}
Traction / Milestones: {traction}
Team:
{team_text}
Funding Ask: {funding_ask}
Use of Funds: {use_of_funds}

YOUR TASK:
Rewrite and polish all the above into concise, investor-friendly slide content.
- Use short, punchy bullet points (max 12 words per bullet)
- Every number/stat must be kept exactly as provided
- Slide titles must be crisp (3–5 words)
- The narrative arc must flow: Problem → Solution → Market → Product → Traction → Team → Ask

Return ONLY a valid JSON object. No markdown. No explanation. No preamble.
The JSON must follow this exact schema:

{{
  "cover": {{
    "company_name": "{company_name}",
    "tagline": "one punchy line (max 10 words)",
    "founder_name": "{founder_name}",
    "subtitle": "Investor Presentation"
  }},
  "problem": {{
    "slide_title": "The Problem",
    "headline": "one bold problem statement sentence",
    "bullets": ["bullet 1", "bullet 2", "bullet 3"]
  }},
  "solution": {{
    "slide_title": "Our Solution",
    "headline": "one bold solution statement sentence",
    "bullets": ["bullet 1", "bullet 2", "bullet 3"]
  }},
  "market": {{
    "slide_title": "Market Opportunity",
    "headline": "one bold market opportunity statement",
    "tam": "Total Addressable Market figure or description",
    "sam": "Serviceable Addressable Market figure or description",
    "som": "Serviceable Obtainable Market figure or description"
  }},
  "product": {{
    "slide_title": "Our Product",
    "headline": "one bold product description sentence",
    "features": [
      {{"icon_label": "short label", "description": "1 line description"}},
      {{"icon_label": "short label", "description": "1 line description"}},
      {{"icon_label": "short label", "description": "1 line description"}}
    ]
  }},
  "traction": {{
    "slide_title": "Traction & Milestones",
    "headline": "one bold traction statement",
    "metrics": [
      {{"label": "metric name", "value": "number or stat"}},
      {{"label": "metric name", "value": "number or stat"}},
      {{"label": "metric name", "value": "number or stat"}}
    ],
    "milestones": ["milestone 1", "milestone 2", "milestone 3"]
  }},
  "team": {{
    "slide_title": "Our Team",
    "headline": "one bold team strength statement",
    "members": [
      {{"name": "name", "role": "role", "highlight": "one key credential or achievement"}}
    ]
  }},
  "ask": {{
    "slide_title": "The Ask",
    "headline": "one bold funding ask statement",
    "amount": "funding amount",
    "use_of_funds": [
      {{"area": "area name", "percentage": "xx%", "description": "short description"}},
      {{"area": "area name", "percentage": "xx%", "description": "short description"}},
      {{"area": "area name", "percentage": "xx%", "description": "short description"}}
    ],
    "closing_line": "one inspiring closing sentence"
  }}
}}
""".strip()

    return prompt


# ---------------------------------------------------------------------------
# JSON extractor — handles model quirks (thinking tags, markdown fences)
# ---------------------------------------------------------------------------

def _extract_json(raw: str) -> dict:
    """
    Robustly extract a JSON object from the model's raw output.
    The AIService sometimes wraps output in <think>...</think> blocks
    or markdown code fences — we strip those first.
    """
    # Remove <think>...</think> blocks (Qwen/DeepSeek thinking tokens)
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)

    # Strip markdown fences
    raw = re.sub(r"```(?:json)?", "", raw).strip()
    raw = raw.strip("`").strip()

    # Find the first { ... } block
    start = raw.find("{")
    end   = raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON object found in AI response")

    json_str = raw[start:end]
    return json.loads(json_str)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_slide_content(form_data: dict) -> dict:
    """
    Call AIService with the pitch deck prompt and return structured slide content.

    Args:
        form_data: dict of founder-provided form fields

    Returns:
        dict following the slide schema above

    Raises:
        ValueError: if the AI response cannot be parsed as valid JSON
        Exception:  propagates any AIService errors
    """
    prompt = _build_prompt(form_data)

    logger.info(f"[PitchDeck] Generating content for: {form_data.get('company_name', 'unknown')}")

    raw_result = AIService.generate(
        feature="pitch_deck",
        user_input=prompt,
        temperature=0.6,      # slightly creative but consistent
        max_tokens=2000
    )

    # AIService.generate may return a dict or a string depending on version
    if isinstance(raw_result, dict):
        raw_text = raw_result.get("text") or raw_result.get("response") or json.dumps(raw_result)
    else:
        raw_text = str(raw_result)

    logger.debug(f"[PitchDeck] Raw AI output (first 300 chars): {raw_text[:300]}")

    try:
        content = _extract_json(raw_text)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"[PitchDeck] Failed to parse AI JSON: {e}\nRaw: {raw_text[:500]}")
        raise ValueError(f"AI response was not valid JSON: {e}")

    logger.info(f"[PitchDeck] Content generated successfully for: {form_data.get('company_name')}")
    return content