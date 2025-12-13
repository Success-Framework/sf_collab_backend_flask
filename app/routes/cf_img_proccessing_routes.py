# cf_img_processing_routes.py
from flask import Blueprint, request, jsonify
import requests
import os
import base64
import logging
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create blueprint
cf_bp = Blueprint('cf', __name__, url_prefix='/api/cf')

# Cloudflare configuration
CF_ACCOUNT_ID = os.getenv('CF_ACCOUNT_ID')
CF_API_TOKEN = os.getenv('CF_API_TOKEN')

# Model configurations
MODELS = {
    'flux': '@cf/black-forest-labs/flux-schnell',
    'sdxl': '@cf/bytedance/stable-diffusion-xl-lightning',
    'sd15': '@cf/runwayml/stable-diffusion-v1-5-inpainting',
    
}

def validate_image_parameters(prompt, width, height):
    """Validate image generation parameters"""
    if not prompt or not prompt.strip():
        return "Prompt is required"
    
    if len(prompt.strip()) < 3:
        return "Prompt must be at least 3 characters"
    
    if len(prompt.strip()) > 1000:
        return "Prompt must be less than 1000 characters"
    
    if width < 64 or width > 2048:
        return "Width must be between 64 and 2048 pixels"
    
    if height < 64 or height > 2048:
        return "Height must be between 64 and 2048 pixels"
    
    if width * height > 4194304:  # 2048*2048 = 4MP limit
        return "Image dimensions too large (max 4MP)"
    
    return None

def generate_image(model, prompt, width=1024, height=1024):
    """Helper function to generate images using Cloudflare Workers AI"""
    if not CF_ACCOUNT_ID or not CF_API_TOKEN:
        return {
            'success': False,
            'error': 'Cloudflare credentials not configured. Set CF_ACCOUNT_ID and CF_API_TOKEN environment variables.'
        }
    
    if model not in MODELS:
        return {
            'success': False,
            'error': f'Invalid model. Choose from: {", ".join(MODELS.keys())}'
        }
    
    # Validate parameters
    validation_error = validate_image_parameters(prompt, width, height)
    if validation_error:
        return {
            'success': False,
            'error': validation_error
        }
    
    # Construct Cloudflare API endpoint
    model_name = MODELS[model]
    url = f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{model_name}'
    
    # Prepare headers
    headers = {
        'Authorization': f'Bearer {CF_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Prepare payload with additional parameters for better results
    payload = {
        'prompt': prompt,
        'width': width,
        'height': height,
        'num_steps': 4 if model == 'flux' else 8,  # Fewer steps for faster generation
        'guidance': 7.5,  # Guidance scale for better prompt adherence
    }
    
    try:
        logging.info(f"Generating image with model {model}: {prompt[:50]}...")
        
        # Send request to Cloudflare
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        # Handle rate limiting
        if response.status_code == 429:
            return {
                'success': False,
                'error': 'Rate limit exceeded. Please try again in a few moments.'
            }
        
        # Handle authentication errors
        if response.status_code == 401:
            return {
                'success': False,
                'error': 'Invalid API token. Please check your CF_API_TOKEN.'
            }
        
        # Handle forbidden access
        if response.status_code == 403:
            return {
                'success': False,
                'error': 'Access forbidden. Please verify your CF_ACCOUNT_ID and API token permissions.'
            }
        
        # Handle model unavailable
        if response.status_code == 404:
            return {
                'success': False,
                'error': f'Model {model_name} not found or unavailable.'
            }
        
        # Handle server errors
        if response.status_code >= 500:
            return {
                'success': False,
                'error': 'Cloudflare service temporarily unavailable. Please retry.'
            }
        
        # Check for successful response
        if response.status_code != 200:
            error_data = response.json()
            error_msg = error_data.get('errors', [{'message': 'Unknown error'}])[0].get('message', 'Unknown error')
            return {
                'success': False,
                'error': f'API error: {error_msg}'
            }
        
        # Parse response - Cloudflare returns binary image data
        image_bytes = response.content
        
        if len(image_bytes) == 0:
            return {
                'success': False,
                'error': 'Received empty image data from Cloudflare'
            }
        
        # Convert to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        logging.info(f"Image generated successfully: {len(image_bytes)} bytes")
        
        return {
            'success': True,
            'image': f'data:image/png;base64,{image_base64}',
            'model': model,
            'dimensions': f'{width}x{height}',
            'size': len(image_bytes),
            'timestamp': datetime.now().isoformat()
        }
        
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': 'Request timeout. The model took too long to respond. Try a simpler prompt.'
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'error': 'Network error. Please check your internet connection.'
        }
    except Exception as e:
        logging.error(f"Unexpected error generating image: {str(e)}")
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }

#! HEALTH CHECK
@cf_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    status = 'ready' if CF_ACCOUNT_ID and CF_API_TOKEN else 'no_credentials'
    
    return jsonify({
        'success': True,
        'status': status,
        'models_available': list(MODELS.keys()),
        'account_configured': bool(CF_ACCOUNT_ID),
        'timestamp': datetime.now().isoformat()
    })

#! GET MODELS
@cf_bp.route('/models', methods=['GET'])
def get_models():
    """Get available models"""
    model_details = {
        'flux': {
            'name': 'Flux Schnell',
            'description': 'Best for logos, illustrations, and creative designs',
            'max_resolution': '1024x1024',
            'speed': 'Fast',
            'best_for': ['Logos', 'Illustrations', 'Creative designs']
        },
        'sdxl': {
            'name': 'SDXL Lightning',
            'description': 'Fast realistic images with photographic quality',
            'max_resolution': '1024x1024',
            'speed': 'Very Fast',
            'best_for': ['Photorealistic', 'Portraits', 'Landscapes']
        },
        'sd15': {
            'name': 'Stable Diffusion 1.5',
            'description': 'Classic model for artistic and balanced results',
            'max_resolution': '768x768',
            'speed': 'Moderate',
            'best_for': ['Artistic', 'Stylized', 'Consistent results']
        }
    }
    
    return jsonify({
        'success': True,
        'models': model_details
    })

#! GENERATE IMAGE
@cf_bp.route('/generate', methods=['POST'])
def generate_image_endpoint():
    """Generate image using specified model"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        model = data.get('model', 'flux')
        prompt = data.get('prompt', '')
        width = data.get('width', 1024)
        height = data.get('height', 1024)
        negative_prompt = data.get('negative_prompt', '')
        
        # Generate image
        result = generate_image(model, prompt, width, height)
        
        if not result['success']:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        logging.error(f"Error in generate endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

#! GENERATE WITH SPECIFIC MODEL (backward compatibility)
@cf_bp.route('/generate/<model>', methods=['POST'])
def generate_specific_model(model):
    """Generate image using specific model"""
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing prompt field'
            }), 400
        
        prompt = data['prompt']
        width = data.get('width', 1024)
        height = data.get('height', 1024)
        
        if model not in MODELS:
            return jsonify({
                'success': False,
                'error': f'Invalid model. Choose from: {", ".join(MODELS.keys())}'
            }), 400
        
        # Generate image
        result = generate_image(model, prompt, width, height)
        
        if not result['success']:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        logging.error(f"Error generating with model {model}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500