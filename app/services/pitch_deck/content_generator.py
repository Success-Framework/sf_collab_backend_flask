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
    company_name  = form_data.get("company_name", "")
    tagline       = form_data.get("tagline", "")
    founder_name  = form_data.get("founder_name", "")
    problem       = form_data.get("problem", "")
    solution      = form_data.get("solution", "")
    market_size   = form_data.get("market_size", "")
    product_desc  = form_data.get("product_description", "")
    key_features  = form_data.get("key_features", [])
    traction      = form_data.get("traction", "")
    team_members  = form_data.get("team_members", [])
    funding_ask   = form_data.get("funding_ask", "")
    use_of_funds  = form_data.get("use_of_funds", "")
    template      = form_data.get("template", "general")

    features_text = "\n".join(f"- {f}" for f in key_features if f)
    team_text = "\n".join(
        f"- {m.get('name', '')} ({m.get('role', '')})"
        for m in team_members if m.get("name")
    )

    # /no_think tells Qwen3 to skip its <think> block entirely
    # Build prompt as a list of lines to avoid f-string + triple-quote issues
    lines = [
        "/no_think",
        "",
        "You are an expert startup pitch deck writer.",
        "OUTPUT RULES - FOLLOW EXACTLY:",
        "1. Your entire response must be one valid JSON object.",
        "2. Start your response with { and end with }",
        "3. No <think> block. No markdown. No explanation. No text before or after the JSON.",
        "",
        "Template style: " + template.upper(),
        "Company: " + company_name,
        "Tagline: " + tagline,
        "Founder: " + founder_name,
        "",
        "FOUNDER INPUTS:",
        "Problem: " + problem,
        "Solution: " + solution,
        "Market Size: " + market_size,
        "Product: " + product_desc,
        "Key Features:",
        features_text,
        "Traction: " + traction,
        "Team:",
        team_text,
        "Funding Ask: " + funding_ask,
        "Use of Funds: " + use_of_funds,
        "",
        "TASK: Rewrite the above into concise investor-friendly slide content.",
        "Rules: max 12 words per bullet, keep all numbers exactly as given, crisp 3-5 word slide titles.",
        "",
        "Return this exact JSON structure filled in with real content:",
        "",
        '{',
        '  "cover": {',
        '    "company_name": "' + company_name + '",',
        '    "tagline": "one punchy line max 10 words",',
        '    "founder_name": "' + founder_name + '",',
        '    "subtitle": "Investor Presentation"',
        '  },',
        '  "problem": {',
        '    "slide_title": "The Problem",',
        '    "headline": "one bold problem statement",',
        '    "bullets": ["bullet 1", "bullet 2", "bullet 3"]',
        '  },',
        '  "solution": {',
        '    "slide_title": "Our Solution",',
        '    "headline": "one bold solution statement",',
        '    "bullets": ["bullet 1", "bullet 2", "bullet 3"]',
        '  },',
        '  "market": {',
        '    "slide_title": "Market Opportunity",',
        '    "headline": "one bold market statement",',
        '    "tam": "Total Addressable Market value",',
        '    "sam": "Serviceable Addressable Market value",',
        '    "som": "Serviceable Obtainable Market value"',
        '  },',
        '  "product": {',
        '    "slide_title": "Our Product",',
        '    "headline": "one bold product statement",',
        '    "features": [',
        '      {"icon_label": "label", "description": "one line"},',
        '      {"icon_label": "label", "description": "one line"},',
        '      {"icon_label": "label", "description": "one line"}',
        '    ]',
        '  },',
        '  "traction": {',
        '    "slide_title": "Traction",',
        '    "headline": "one bold traction statement",',
        '    "metrics": [',
        '      {"label": "metric", "value": "stat"},',
        '      {"label": "metric", "value": "stat"},',
        '      {"label": "metric", "value": "stat"}',
        '    ],',
        '    "milestones": ["milestone 1", "milestone 2", "milestone 3"]',
        '  },',
        '  "team": {',
        '    "slide_title": "Our Team",',
        '    "headline": "one bold team statement",',
        '    "members": [',
        '      {"name": "name", "role": "role", "highlight": "key credential"}',
        '    ]',
        '  },',
        '  "ask": {',
        '    "slide_title": "The Ask",',
        '    "headline": "one bold ask statement",',
        '    "amount": "funding amount",',
        '    "use_of_funds": [',
        '      {"area": "area", "percentage": "xx%", "description": "short desc"},',
        '      {"area": "area", "percentage": "xx%", "description": "short desc"},',
        '      {"area": "area", "percentage": "xx%", "description": "short desc"}',
        '    ],',
        '    "closing_line": "one inspiring closing sentence"',
        '  }',
        '}',
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# JSON extractor
# ---------------------------------------------------------------------------

def _extract_json(raw: str) -> dict:
    """
    Robustly extract a JSON object from the model's raw output.
    Handles: <think> blocks (complete and dangling), markdown fences,
    trailing commas, extra text before/after JSON.
    """
    if isinstance(raw, dict):
        return raw

    raw = str(raw)

    # Remove complete <think>...</think> blocks
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
    # Remove dangling <think> that never closed (model hit token limit mid-think)
    raw = re.sub(r"<think>.*", "", raw, flags=re.DOTALL)

    # Strip markdown fences
    raw = re.sub(r"```(?:json)?\s*", "", raw)
    raw = re.sub(r"```", "", raw)
    raw = raw.strip()

    # Find outermost { ... } using brace depth tracking
    start = raw.find("{")
    if start == -1:
        raise ValueError("No JSON object found in AI response")

    depth = 0
    end = -1
    for i in range(start, len(raw)):
        if raw[i] == "{":
            depth += 1
        elif raw[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    if end == -1:
        raise ValueError("JSON object in AI response is not properly closed")

    json_str = raw[start:end]

    # Fix trailing commas before } or ]
    json_str = re.sub(r",\s*}", "}", json_str)
    json_str = re.sub(r",\s*]", "]", json_str)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        try:
            return json.loads(json_str.replace("'", '"'))
        except json.JSONDecodeError:
            raise ValueError(f"Could not parse AI JSON: {e}. Snippet: {json_str[:300]}")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_slide_content(form_data: dict) -> dict:
    """
    Call AIService with the pitch deck prompt and return structured slide content.
    """
    prompt = _build_prompt(form_data)

    logger.info(f"[PitchDeck] Generating content for: {form_data.get('company_name', 'unknown')}")

    raw_result = AIService.generate(
        feature="chat",     # "chat" is the safe key for AIService proxy
        user_input=prompt,
        temperature=0.5,    # lower = more deterministic JSON
        max_tokens=4000     # JSON ~1500 tokens; must leave room beyond thinking
    )

    # AIService.generate may return a dict or a string
    if isinstance(raw_result, dict):
        raw_text = (
            raw_result.get("text")
            or raw_result.get("response")
            or raw_result.get("content")
            or json.dumps(raw_result)
        )
    else:
        raw_text = str(raw_result)

    logger.info(f"[PitchDeck] Raw AI output (first 500 chars): {raw_text[:500]}")

    try:
        content = _extract_json(raw_text)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"[PitchDeck] Failed to parse AI JSON: {e}\nRaw: {raw_text[:800]}")
        raise ValueError(f"AI response was not valid JSON: {e}")

    logger.info(f"[PitchDeck] Content generated successfully for: {form_data.get('company_name')}")
    return content