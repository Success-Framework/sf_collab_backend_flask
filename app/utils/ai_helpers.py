from flask import current_app
from groq import Groq
import re
import json
from openai import OpenAI
from weasyprint import HTML
import markdown
def get_groq_client():
    key = current_app.config.get("GROQ_API_KEY")
    return Groq(api_key=key) if key else None

def get_openai_client():
    key = current_app.config.get("OPENAI_API_KEY")
    return OpenAI(api_key=key) if key else None

def extract_text_from_response(response, *, expect_json=False, strict=False):
    texts = []

    for item in getattr(response, "output", []):
        # item is ResponseOutputMessage
        for content in getattr(item, "content", []):
            # content is ResponseOutputText / tool calls / etc
            if getattr(content, "type", None) == "output_text":
                text = getattr(content, "text", "").strip()
                if text:
                    texts.append(text)

    if not texts:
        return [] if expect_json else ""

    combined = "\n".join(texts).strip()

    if not expect_json:
        return combined

    # --- JSON sanitation ---
    cleaned = re.sub(r"^```(?:json)?|```$", "", combined, flags=re.IGNORECASE).strip()

    match = re.search(r"(\{.*\}|\[.*\])", cleaned, re.DOTALL)
    if not match:
        if strict:
            raise ValueError("No JSON found in model response")
        return cleaned

    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as e:
        if strict:
            raise ValueError(f"Invalid JSON from model: {e}")
        return match.group(1)


def generate_pdf_from_markdown(markdown_text, output_path):
    html = markdown.markdown(
        markdown_text,
        extensions=["extra", "tables", "fenced_code"]
    )

    styled_html = f"""
    <html>
    <head>
      <style>
        body {{
          font-family: Arial, sans-serif;
          line-height: 1.6;
          padding: 40px;
        }}
        h1, h2, h3 {{
          color: #1a1a1a;
        }}
        table {{
          width: 100%;
          border-collapse: collapse;
        }}
        th, td {{
          border: 1px solid #ddd;
          padding: 8px;
        }}
        th {{
          background-color: #f4f4f4;
        }}
      </style>
    </head>
    <body>
      {html}
    </body>
    </html>
    """

    HTML(string=styled_html).write_pdf(output_path)

def get_response(model, system_prompt, user_prompt, temperature=0.7, max_tokens=2048):
    if model == 'qwen/qwen3-32b':
        groq_client = get_groq_client()
        max_tokens = min(max_tokens, 4096)
        completion = groq_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        response_text = completion.choices[0].message.content
        tokens_used = getattr(completion.usage, "total_tokens", None)
    # =========================
    # OPENAI (RESPONSES API)
    # =========================
    elif model == 'openai/gpt-oss-20b':
        client = get_openai_client()
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": [
                        {"type": "input_text", "text": system_prompt}
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": user_prompt}
                    ],
                },
            ],
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        response_text = extract_text_from_response(response, expect_json=False)
        tokens_used = getattr(response.usage, "output_tokens", None)

    else:
        raise ValueError(f"Unsupported model: {model}")
    return response_text, tokens_used