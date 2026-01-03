import os
import uuid
import json
from flask import Blueprint, request, jsonify, send_file
from dotenv import load_dotenv
from groq import Groq
from werkzeug.utils import secure_filename
from pathlib import Path
import logging
from datetime import datetime
import requests

# Load environment variables
load_dotenv()

# Create blueprint
qwen_bp = Blueprint('qwen', __name__)

# Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
QWN_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'qwen_generated')  # Changed name

# Create upload folder
Path(QWN_UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

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
@qwen_bp.route('/health', methods=['GET'])
def qwen_health():
    """Health check endpoint"""
    try:
        status = {
            'status': 'ready' if GROQ_API_KEY else 'no_api_key',
            'version': '1.0.0',
            'models_available': len(AVAILABLE_MODELS),
            'timestamp': datetime.now().isoformat()
        }
        return standard_response(True, status)
    except Exception as e:
        logging.error(f'Health check error: {str(e)}')
        return standard_response(False, None, str(e), 500)

#! GET AVAILABLE MODELS
@qwen_bp.route('/models', methods=['GET'])
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
@qwen_bp.route('/generate', methods=['POST'])
def qwen_generate():
    """Generate content (chat, business plan, pitch deck) with structured JSON output"""
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return standard_response(False, None, 'Missing prompt in request', 400)
        
        prompt = data.get('prompt')
        model = data.get('model', AVAILABLE_MODELS[0])
        content_type = data.get('content_type', 'chat')  # chat, business_plan, pitch_deck
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 2048)
        output_format = data.get('output_format', 'text')  # text, json
        
        if model not in AVAILABLE_MODELS:
            return standard_response(False, None, f'Model not available. Choose from: {AVAILABLE_MODELS}', 400)
        
        if not GROQ_API_KEY and model == 'qwen/qwen3-32b':
            return standard_response(False, None, 'Groq API key not configured', 500)
        
        if not OPENAI_API_KEY and model == 'openai/gpt-oss-20b':
            return standard_response(False, None, 'OpenAI API key not configured', 500)
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
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            data = response.json()
            response_text = data["choices"][0]["message"]["content"]

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
@qwen_bp.route('/download/<filename>', methods=['GET'])
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