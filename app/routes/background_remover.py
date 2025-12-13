from datetime import datetime
import os
import uuid
from flask import Blueprint, request, jsonify, send_file
from rembg import remove
from PIL import Image, ImageEnhance, ImageFilter
from werkzeug.utils import secure_filename
from pathlib import Path
import logging

# Create blueprint
background_bp = Blueprint('background', __name__, url_prefix='/api/background-remover')

# Configuration
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
BG_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'background_removed')  # Changed name
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Create upload folder
Path(BG_UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file, max_size=MAX_FILE_SIZE):
    """Validate file size"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= max_size

def generate_filename(extension='png'):
    return f"{uuid.uuid4().hex}.{extension}"

def standard_response(success=True, data=None, error=None, code=200):
    response = jsonify({
        'success': success,
        'data': data,
        'error': error
    })
    return response, code

# ============================================================
# BACKGROUND REMOVER ROUTES
# ============================================================

#! HEALTH CHECK
@background_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return standard_response(True, {
            'status': 'ready',
            'timestamp': datetime.now().isoformat(),
            'max_file_size': MAX_FILE_SIZE,
            'allowed_extensions': list(ALLOWED_EXTENSIONS)
        })
    except Exception as e:
        logging.error(f'Health check error: {str(e)}')
        return standard_response(False, None, str(e), 500)

#! GET AVAILABLE MODELS
@background_bp.route('/models', methods=['GET'])
def background_models():
    """Get available background removal models"""
    try:
        models = ['general', 'anime', 'portrait', 'product']
        return standard_response(True, {'models': models})
    except Exception as e:
        logging.error(f'Error getting models: {str(e)}')
        return standard_response(False, None, str(e), 500)

#! REMOVE BACKGROUND
@background_bp.route('/remove', methods=['POST'])
def remove_background():
    """Remove background from image"""
    try:
        if 'image' not in request.files:
            return standard_response(False, None, 'No image file provided', 400)
        
        file = request.files['image']
        
        if file.filename == '':
            return standard_response(False, None, 'No selected file', 400)
        
        if not allowed_file(file.filename):
            return standard_response(False, None, 'Invalid file type. Use PNG, JPG, or WEBP', 400)
        
        if not validate_file_size(file):
            return standard_response(False, None, f'File size exceeds maximum limit of {MAX_FILE_SIZE / (1024*1024)}MB', 400)
        
        # Get parameters
        model = request.form.get('model', 'general')
        enhance = request.form.get('enhance', 'false').lower() == 'true'
        output_format = request.form.get('format', 'png')
        
        # Read image
        input_image = Image.open(file.stream)
        
        # Remove background
        output_image = remove(input_image)
        
        # Enhance if requested
        if enhance:
            # Simple enhancement: increase contrast and sharpness
            enhancer = ImageEnhance.Contrast(output_image)
            output_image = enhancer.enhance(1.2)
            output_image = output_image.filter(ImageFilter.SHARPEN)
        
        # Convert format if needed
        if output_format.lower() != 'png':
            if output_format.lower() == 'jpg' or output_format.lower() == 'jpeg':
                # Create white background for JPEG
                background = Image.new('RGB', output_image.size, (255, 255, 255))
                background.paste(output_image, mask=output_image.split()[3] if output_image.mode == 'RGBA' else None)
                output_image = background
        
        # Save to upload folder
        filename = generate_filename(output_format)
        filepath = os.path.join(BG_UPLOAD_FOLDER, filename)  # Use BG_UPLOAD_FOLDER
        output_image.save(filepath, format=output_format.upper() if output_format != 'jpg' else 'JPEG')
        
        # Return URL
        image_url = f"/api/background-remover/download/{filename}"
        
        return standard_response(True, {
            'image_url': image_url,
            'filename': filename,
            'format': output_format,
            'size': os.path.getsize(filepath),
            'model_used': model,
            'enhanced': enhance,
            'dimensions': f'{output_image.width}x{output_image.height}'
        })
    
    except Exception as e:
        logging.error(f'Background removal error: {str(e)}')
        return standard_response(False, None, str(e), 500)

#! DOWNLOAD PROCESSED IMAGE
@background_bp.route('/download/<filename>', methods=['GET'])
def download_processed_image(filename):
    """Download processed image"""
    try:
        filepath = os.path.join(BG_UPLOAD_FOLDER, secure_filename(filename))  # Use BG_UPLOAD_FOLDER
        
        if not os.path.exists(filepath):
            return standard_response(False, None, 'File not found', 404)
        
        # Determine MIME type
        ext = filename.split('.')[-1].lower()
        mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'webp': 'image/webp'
        }
        
        return send_file(
            filepath,
            mimetype=mime_types.get(ext, 'image/png'),
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        logging.error(f'Download error: {str(e)}')
        return standard_response(False, None, str(e), 500)