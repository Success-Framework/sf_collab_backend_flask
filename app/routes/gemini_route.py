from flask import Blueprint, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create blueprint
gemini_bp = Blueprint('gemini', __name__, url_prefix='/api/gemini')

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

@gemini_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy', 
        'service': 'gemini-api',
        'model': 'gemini-2.0-flash'
    }), 200

@gemini_bp.route('/chat', methods=['POST'])
def gemini_chat():
    """
    Endpoint for chatting with Gemini AI
    Expected JSON: {"prompt": "your message here"}
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                'success': False,
                'error': 'No prompt provided. Please provide a prompt in the request body.'
            }), 400
        
        prompt = data['prompt'].strip()
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt cannot be empty'
            }), 400
        
        # Optional parameters
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 1000)
        
        # Generate response using Gemini
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": max_tokens,
        }
        
        response = gemini_model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return jsonify({
            'success': True,
            'response': response.text,
            'prompt': prompt,
            'model': 'gemini-2.0-flash',
            'temperature': temperature,
            'max_tokens': max_tokens
        }), 200
    
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to generate response'
        }), 500

@gemini_bp.route('/models', methods=['GET'])
def list_models():
    """List available Gemini models"""
    try:
        models = genai.list_models()
        model_names = [model.name for model in models]
        
        return jsonify({
            'success': True,
            'models': model_names,
            'count': len(model_names)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@gemini_bp.route('/analyze-image', methods=['POST'])
def analyze_image():
    """
    Analyze image with Gemini Vision
    Expected: multipart/form-data with 'image' file and optional 'prompt'
    """
    try:
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Optional custom prompt
        prompt = request.form.get('prompt', 'Describe this image in detail')
        
        # Read image
        image_bytes = file.read()
        
        # Use Gemini Vision model
        vision_model = genai.GenerativeModel('gemini-pro-vision')
        
        # Prepare content
        image_part = {
            "mime_type": file.content_type or 'image/jpeg',
            "data": image_bytes
        }
        
        # Generate response
        response = vision_model.generate_content([prompt, image_part])
        
        return jsonify({
            'success': True,
            'response': response.text,
            'prompt': prompt,
            'model': 'gemini-pro-vision'
        }), 200
    
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500