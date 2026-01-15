import os
import uuid
import json
import re
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from openai import OpenAI
import base64
from app.models.user import User
from app.extensions import db
from flask import Blueprint, request, jsonify, send_file
from dotenv import load_dotenv
from groq import Groq
from werkzeug.utils import secure_filename
from pathlib import Path
import logging
from datetime import datetime
import requests
# from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.services.ai_assistant.ingest import ingest_document
from app.services.ai_assistant.rag import ask_assistant
# Load environment variables
load_dotenv()

# Create blueprint
ai_bp = Blueprint('qwen', __name__)

# Configuration
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
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
QWN_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'qwen_generated')  # Changed name

# Create upload folder
Path(QWN_UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

# Available models
AVAILABLE_MODELS = [
    "openai/gpt-oss-20b",
    "qwen/qwen3-32b"
]

def standard_response(success=True, data=None, error=None, code=200):
    response = jsonify({
        'success': success,
        'data': data,
        'error': error
    })
    return response, code

# ============================================================
# QWEN ROUTES
# ============================================================

#! HEALTH CHECK
@ai_bp.route('/health', methods=['GET'])
def qwen_health():
    """Health check endpoint"""
    OPENAI_API_KEY = current_app.config.get("OPENAI_API_KEY")
    GROQ_API_KEY = current_app.config.get("GROQ_API_KEY")
    try:
        status = {
            'status': 'ready' if GROQ_API_KEY or OPENAI_API_KEY else 'no_api_key',
            'openai_api_key': bool(OPENAI_API_KEY),
            'groq_api_key': bool(GROQ_API_KEY),
            'version': '1.0.0',
            'models_available': len(AVAILABLE_MODELS),
            'timestamp': datetime.now().isoformat()
        }
        return standard_response(True, status)
    except Exception as e:
        logging.error(f'Health check error: {str(e)}')
        return standard_response(False, None, str(e), 500)

#! GET AVAILABLE MODELS
@ai_bp.route('/models', methods=['GET'])
def get_models():
    """Get available models"""
    try:
        # Add model details
        model_details = {
            'openai/gpt-oss-20b': {
                'name': 'GPT-OSS-20B',
                'description': 'OpenAI 20B parameter model for general tasks',
                'max_tokens': 2048
            },
            'qwen/qwen3-32b': {
                'name': 'Qwen 3 32B',
                'description': 'Advanced Qwen model with 32B parameters',
                'max_tokens': 4096
            }
        }
        return standard_response(True, {
            'models': AVAILABLE_MODELS,
            'model_details': model_details
        })
    except Exception as e:
        logging.error(f'Error getting models: {str(e)}')
        return standard_response(False, None, str(e), 500)

#! GENERATE CONTENT
#! GENERATE CONTENT
@ai_bp.route('/generate', methods=['POST', 'OPTIONS'])
def qwen_generate():
    """Generate content (chat, business plan, pitch deck) with structured JSON output"""
    try:
        if request.method == 'OPTIONS':
            return standard_response(True, {}, code=200)
        data = request.get_json()

        if not data or 'prompt' not in data:
            return standard_response(False, None, 'Missing prompt in request', 400)
        OPENAI_API_KEY = current_app.config.get("OPENAI_API_KEY")
        GROQ_API_KEY = current_app.config.get("GROQ_API_KEY")
        groq_client = get_groq_client()

        prompt = data.get('prompt')
        model = data.get('model', AVAILABLE_MODELS[0])
        content_type = data.get('content_type', 'chat')  # chat, business_plan, pitch_deck
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 2048)
        output_format = data.get('output_format', 'text')  # text, json
        
        if model not in AVAILABLE_MODELS:
            return standard_response(False, None, f'Model not available. Choose from: {AVAILABLE_MODELS}', 400)
        
        client = None
        if model == 'qwen/qwen3-32b':
            client = get_groq_client()
        elif model == 'openai/gpt-oss-20b':
            client = get_openai_client()

        if not client:
            return standard_response(False, None, 'API key not configured for selected model', 500)
        # Simplified system prompts
        system_prompts = {
            'chat': '''You are a helpful and professional AI assistant. Provide accurate, detailed, and well-structured responses in Markdown format.''',
            
            'business_plan': '''You are an expert business consultant specializing in startup development. 
            Generate a comprehensive, professional business plan in Markdown format.
            
            Include these sections:
            1. Executive Summary
            2. Company Description
            3. Market Analysis
            4. Products & Services
            5. Marketing Strategy
            6. Operations Plan
            7. Management Team
            8. Financial Projections
            9. Funding Needs
            10. Risk Analysis
            
            Use proper Markdown formatting with headers, lists, tables where appropriate.
            Include realistic numbers and data.''',
            
            'pitch_deck': '''You are a pitch deck expert and venture capital advisor. 
            Generate compelling, investor-ready pitch deck content in Markdown format.
            
            Structure it as a pitch deck with these slides:
            1. Title Slide
            2. The Problem
            3. The Solution
            4. Market Opportunity
            5. Product
            6. Business Model
            7. Traction
            8. Competition
            9. Team
            10. Financials
            11. Funding Ask
            12. Contact
            
            Use proper Markdown formatting. Make it visually descriptive and include quantifiable metrics.'''
        }
        
        system_prompt = system_prompts.get(content_type, system_prompts['chat'])
        
        # Enhance prompt based on content type
        if content_type == 'business_plan':
            enhanced_prompt = f"""Create a comprehensive, investor-ready business plan for: {prompt}
            
            Please include:
            1. Specific, quantifiable data where applicable
            2. Realistic financial projections
            3. Detailed market analysis
            4. Clear operational plans
            5. Risk assessment and mitigation strategies
            
            Format the response in Markdown with clear sections and proper formatting."""
            
        elif content_type == 'pitch_deck':
            enhanced_prompt = f"""Create a compelling, investor-focused pitch deck for: {prompt}
            
            Requirements:
            1. Make it visually descriptive (imagine each slide's content)
            2. Include quantifiable metrics and projections
            3. Highlight competitive advantages clearly
            4. Focus on traction and proof points
            5. Structure for a 10-12 minute presentation
            
            Format the response in Markdown with slide titles and bullet points."""
            
        else:
            enhanced_prompt = prompt
        response_text = ""
        if model == 'qwen/qwen3-32b' and content_type in ['business_plan', 'pitch_deck']:
            max_tokens = min(max_tokens, 4096)

            # Call Groq API - REMOVE response_format for now to avoid JSON validation issues
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": enhanced_prompt}
                ],
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
                # Remove response_format to avoid JSON validation errors
                # response_format={"type": "json_object"} if content_type in ['business_plan', 'pitch_deck'] else None
            )
            response_text = chat_completion.choices[0].message.content
        
        elif model == 'openai/gpt-oss-20b':
            # Call OpenAI API directly
            headers = {
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            }

            payload = {
                "model": "gpt-4.1-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": [
                            {"type": "text", "text": system_prompt}
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": enhanced_prompt}
                        ]
                    }
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=enhanced_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            test_responses = extract_text_from_response(response, expect_json=True, strict=True)


            chat_completion = response.json()
        
        
        # Generate downloadable content
        download_formats = ['txt', 'md']
        download_links = {}
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for fmt in download_formats:
            filename = f"{content_type}_{timestamp}.{fmt}"
            filepath = os.path.join(QWN_UPLOAD_FOLDER, filename)
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    if fmt == 'md':
                        f.write(f"# {content_type.replace('_', ' ').title()}\n\n")
                        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"**Model:** {model}\n")
                        f.write(f"**Prompt:** {prompt[:200]}...\n\n")
                        f.write("---\n\n")
                        f.write(response_text)
                    else:  # txt
                        f.write(response_text)
                
                download_links[fmt] = f"/api/qwen/download/{filename}"
                
            except Exception as e:
                logging.error(f"Error creating {fmt} file: {str(e)}")
        
        return standard_response(True, {
            'response': response_text,  # Return as text, not parsed JSON
            'model': model,
            'content_type': content_type,
            'download_links': download_links,
            'timestamp': datetime.now().isoformat(),
            'tokens_used': chat_completion.usage.total_tokens if hasattr(chat_completion, 'usage') else None,
            'format': 'markdown'
        })
    
    except Exception as e:
        logging.error(f'Generation error: {str(e)}')
        return standard_response(False, None, str(e), 500)
        
### Chat 
@ai_bp.route('/chat', methods=['POST', 'OPTIONS'])
def qwen_chat():
    """
    Chat-style endpoint compatible with frontend QwenChat.jsx
    """
    try:
        if request.method == 'OPTIONS':
            return standard_response(True, {}, code=200)
        data = request.get_json()

        if not data or 'messages' not in data:
            return standard_response(False, None, 'Missing messages in request', 400)

        GROQ_API_KEY = current_app.config.get("GROQ_API_KEY")
        groq_client = get_groq_client()
        messages = data.get('messages', [])
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 2048)
        model = data.get('model', AVAILABLE_MODELS[0])

        if not GROQ_API_KEY:
            return standard_response(False, None, 'Groq API key not configured', 500)

        # ---- Convert messages[] → prompt ----
        prompt_lines = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if content:
                prompt_lines.append(f"{role.capitalize()}: {content}")

        final_prompt = "\n".join(prompt_lines) + "\nAssistant:"

        # ---- Call Groq ----
        completion = groq_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": final_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        response_text = completion.choices[0].message.content

        return standard_response(True, {
            "response": response_text,
            "model": model
        })

    except Exception as e:
        logging.exception("Qwen chat error")
        return standard_response(False, None, str(e), 500)

        
# Helper methods to add to your class
def _json_to_markdown(self, data, level=1):
    """Convert JSON structure to Markdown"""
    markdown = ""
    if isinstance(data, dict):
        for key, value in data.items():
            header = "#" * level
            if isinstance(value, (dict, list)):
                markdown += f"{header} {key.replace('_', ' ').title()}\n\n"
                markdown += self._json_to_markdown(value, level + 1)
            else:
                markdown += f"**{key.replace('_', ' ').title()}:** {value}\n\n"
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                markdown += self._json_to_markdown(item, level)
            else:
                markdown += f"- {item}\n"
        markdown += "\n"
    else:
        markdown += f"{data}\n\n"
    return markdown

def _json_to_text(self, data, indent=0):
    """Convert JSON structure to readable text"""
    text = ""
    indent_str = "  " * indent
    
    if isinstance(data, dict):
        for key, value in data.items():
            text += f"{indent_str}{key.replace('_', ' ').title()}:\n"
            text += self._json_to_text(value, indent + 1)
    elif isinstance(data, list):
        for i, item in enumerate(data, 1):
            text += f"{indent_str}{i}. "
            if isinstance(item, (dict, list)):
                text += "\n" + self._json_to_text(item, indent + 1)
            else:
                text += f"{item}\n"
    else:
        text += f"{indent_str}{data}\n"
    
    return text
    
    
#! DOWNLOAD GENERATED CONTENT
@ai_bp.route('/download/<filename>', methods=['GET'])
def download_content(filename):
    """Download generated content"""
    try:
        filepath = os.path.join(QWN_UPLOAD_FOLDER, secure_filename(filename))  # Use QWN_UPLOAD_FOLDER
        
        if not os.path.exists(filepath):
            return standard_response(False, None, 'File not found', 404)
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
    
    except Exception as e:
        logging.error(f'Download error: {str(e)}')
        return standard_response(False, None, str(e), 500)



@ai_bp.route("/logo/generate", methods=["POST", "OPTIONS"])
@jwt_required()
def generate_logo():
    if request.method == 'OPTIONS':
        return standard_response(True, {}, code=200)
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    brand_name = data.get("brandName")
    industry = data.get("industry", "technology")
    style = data.get("style", "minimal")
    colors = data.get("colors", [])
    logo_type = "icon + wordmark"
    additional_notes = data.get("additionalNotes", "")
    subtitle = data.get("subtitle", "")
    symbol = data.get("symbol", "abstract")
    if not brand_name:
        return jsonify({"error": "brandName is required"}), 400

    COST_PER_IMAGE = 50
    IMAGE_COUNT = data.get("imagesAmount", 2)

    total_cost = COST_PER_IMAGE * IMAGE_COUNT

    if user.credits < total_cost:
        return jsonify({"error": "Not enough credits"}), 402
    
    client = get_openai_client()
    slogan_prompt = f"""
        You are a professional brand designer.

        Return ONLY valid JSON.
        Do not include markdown.
        Do not include explanations.
        Do not include comments.

        Schema:
        [
        {{
            "font_family": "string",
            "font_weight": number,
            "letter_spacing": number,
            "text_case": "uppercase | title | sentence",
            "alignment": "center | left",
            "placement": "below | right | stacked",
            "mood": "string"
        }}
        ]

        Brand name: {brand_name}
        Slogan: "{subtitle}"
        Industry: {industry}
        Style: {style}
        Additional notes: {additional_notes}

        Generate exactly 4 variants.
        """
    slogan_responses = []
    try:
        slogan_response = client.responses.create(
            model="gpt-4.1-mini",
            input=slogan_prompt
        )
        slogan_responses = extract_text_from_response(slogan_response, expect_json=True, strict=True)

        if not slogan_responses:
            raise ValueError("Empty slogan response")
    except Exception as e:
        return jsonify({"error": f"Slogan generation failed: {str(e)}"}), 500


    prompt = f"""
        You are a world-class brand identity designer creating a professional startup logo.

        TASK:
        Create a PREMIUM vector logo SYMBOL (ICON ONLY).
        NO text. NO letters. NO slogan.

        BRAND CONTEXT:
        - Brand name: "{brand_name}" (for concept inspiration only — DO NOT RENDER TEXT)
        - Industry: {industry}
        - Style direction: {style}
        - Symbol concept: {symbol}
        - Color palette: {", ".join(colors) if colors else "black and white"}
        - Additional notes: {additional_notes}

        DESIGN REQUIREMENTS:
        - Icon must be abstract, distinctive, and scalable
        - Must work at very small sizes (favicon-ready)
        - Strong silhouette, simple geometry
        - Balanced proportions
        - Professional, modern, startup-ready

        STRICT RULES:
        - NO text
        - NO letters
        - NO numbers
        - NO gradients
        - NO shadows
        - NO 3D
        - NO mockups
        - NO backgrounds or scenes
        - NO UI frames

        STYLE:
        - Flat vector design
        - Clean geometric shapes
        - Consistent stroke or solid fills
        - SVG-style iconography
        - High contrast
        - Minimal visual noise

        COMPOSITION:
        - Centered
        - Isolated symbol
        - Transparent or pure white background
        - Plenty of padding around the icon

        OUTPUT QUALITY:
        - Crisp edges
        - Logo system quality (not illustration)
        - Looks suitable for branding, app icon, and print

        Think like a senior brand designer, not an illustrator.
        """



    

    try:
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            n=IMAGE_COUNT,
            background="transparent"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    images = []

    for img in response.data:
        image_id = str(uuid.uuid4())
        images.append({
            "id": image_id,
            "base64": img.b64_json
        })

    user.credits -= total_cost
    db.session.commit()

    return jsonify({
        "success": True,
        "cost": total_cost,
        "images": images,
        "slogan_designs": slogan_responses
    }), 200

@ai_bp.route("/assistant/documents", methods=["POST"])
@jwt_required()
def upload_document():
    if "file" not in request.files:
        return {"error": "No file provided"}, 400
    
    file = request.files["file"]
    if file.filename == "":
        return {"error": "Empty filename"}, 400

    if not file.filename.lower().endswith((".pdf", ".doc", ".docx")):
        return {"error": "Unsupported file type"}, 400

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)
    file.save(file_path)

    result = ingest_document(file_path)

    return jsonify({
        "success": True,
        "message": "Document indexed successfully",
        "data": result
    })

@ai_bp.route("/assistant/query", methods=["POST"])
@jwt_required()
def assistant_query():
    data = request.get_json()

    if not data or "question" not in data:
        return standard_response(False, None, "Missing question", 400)

    question = data.get("question", "").strip()
    if not question:
        return standard_response(False, None, "Empty question", 400)

    answer = ask_assistant(question)
    print("Assistant answer:", answer)
    return standard_response(True, {
        "answer": answer
    })


# @ai_bp.route("/logo/generate", methods=["POST", "OPTIONS"])
# @jwt_required()
# def generate_logo():
#     if request.method == "OPTIONS":
#         return standard_response(True, {}, code=200)

#     user_id = get_jwt_identity()
#     user = User.query.get(user_id)

#     if not user:
#         return jsonify({"error": "Unauthorized"}), 401

#     data = request.get_json()

#     brand_name = data.get("brandName")
#     industry = data.get("industry", "technology")
#     style = data.get("style", "minimal")
#     colors = data.get("colors", [])
#     additional_notes = data.get("additionalNotes", "")
#     subtitle = data.get("subtitle", "")
#     symbol = data.get("symbol", "abstract")

#     if not brand_name:
#         return jsonify({"error": "brandName is required"}), 400

#     LOGO_COUNT = 4
#     COST_PER_LOGO = 10
#     total_cost = LOGO_COUNT * COST_PER_LOGO

#     # if user.credits < total_cost:
#     #     return jsonify({"error": "Not enough credits"}), 402

#     palette = ", ".join(colors) if colors else "black and white"

#     prompt = f"""
# You are a professional logo designer.

# Generate {LOGO_COUNT} DIFFERENT LOGO SYMBOLS as PURE SVG.

# CRITICAL RULES:
# - DO NOT include any text
# - DO NOT include brand name
# - DO NOT include subtitle
# - DO NOT use <text> tags
# - SYMBOL / ICON ONLY
# - Flat
# - Vector
# - Minimal
# - Transparent background
# - Centered
# - Clean geometry
# - Use only <path>, <rect>, <circle>, <polygon>

# Brand context (for inspiration only):
# Name: {brand_name}
# Industry: {industry}
# Style: {style}
# Symbol idea: {symbol}
# Colors: {palette}

# Wrap each SVG between:
# <!-- LOGO START -->
# <!-- LOGO END -->
# """


#     client = get_openai_client()

#     try:
#         response = client.responses.create(
#             model="gpt-4.1-mini",
#             input=prompt
#         )
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

#     text_output = response.output_text or ""

#     # Extract SVG blocks
#     svg_blocks = re.findall(
#         r"<!-- LOGO START -->(.*?)<!-- LOGO END -->",
#         text_output,
#         re.DOTALL
#     )

#     images = []

#     for svg in svg_blocks[:LOGO_COUNT]:
#         images.append({
#             "id": str(uuid.uuid4()),
#             "svg": svg.strip()
#         })

#     if not images:
#         return jsonify({"error": "No SVGs generated"}), 500

#     # user.credits -= total_cost
#     # db.session.commit()

#     return jsonify({
#         "success": True,
#         "type": "svg",
#         "count": len(images),
#         "cost": total_cost,
#         "images": images
#     }), 200