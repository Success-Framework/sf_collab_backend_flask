from flask import Blueprint, request, send_file, jsonify
from rembg import remove, new_session
from PIL import Image, ImageEnhance
import io
import os
import numpy as np
import cv2

# Create blueprint
bg_remover_bp = Blueprint('background_remover', __name__, url_prefix='/api/background-remover')

import onnxruntime as ort
ort.set_default_logger_severity(3) 
# Create session with models for different use cases
# Create session with CPU
sessions = {
    "general": new_session(model_name="isnet-general-use", providers=["CPUExecutionProvider"]),
}

# Default session
default_session = sessions["general"]

@bg_remover_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy', 
        'service': 'background-remover',
        'models_loaded': list(sessions.keys())
    }), 200

@bg_remover_bp.route('/remove', methods=['POST'])
def remove_background():
    """
    Remove background from image
    Expected: multipart/form-data with 'image' file
    Optional parameters: model, enhance, format
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
        
        # Get optional parameters
        model_type = request.form.get('model', 'general')
        enhance = request.form.get('enhance', 'false').lower() == 'true'
        output_format = request.form.get('format', 'png').lower()
        
        # Select session based on model type
        session = sessions.get(model_type, default_session)
        
        # Open and convert image to RGBA
        img = Image.open(file.stream)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert("RGBA")
        
        # Remove background using the session
        result = remove(img, session=session)
        
        # Enhance image if requested
        if enhance:
            result = enhance_image(result)
        
        # Convert to desired format
        if output_format == 'jpg' or output_format == 'jpeg':
            # Convert RGBA to RGB for JPEG
            if result.mode == 'RGBA':
                background = Image.new('RGB', result.size, (255, 255, 255))
                background.paste(result, mask=result.split()[3])  # 3 is the alpha channel
                result = background
        
        # Save to bytes buffer
        img_io = io.BytesIO()
        
        if output_format in ['jpg', 'jpeg']:
            result.save(img_io, 'JPEG', quality=95)
            mimetype = 'image/jpeg'
        else:
            result.save(img_io, 'PNG', optimize=True)
            mimetype = 'image/png'
        
        img_io.seek(0)
        
        return send_file(
            img_io,
            mimetype=mimetype,
            as_attachment=True,
            download_name=f'no_bg_{file.filename}.{output_format}'
        )
    
    except Exception as e:
        print(f"Error processing image: {e}")
        return jsonify({
            'success': False,
            'error': str(e), 
            'message': 'Failed to remove background'
        }), 500

@bg_remover_bp.route('/models', methods=['GET'])
def list_models():
    """List available background removal models"""
    return jsonify({
        'success': True,
        'models': list(sessions.keys()),
        'description': {
            'portrait': 'Optimized for portraits and human faces',
            'general': 'General purpose, works for most images',
            'anime': 'Optimized for anime/cartoon images',
            'cloth': 'Optimized for clothing/fashion items'
        }
    }), 200

def enhance_image(image):
    """Enhance image quality after background removal"""
    try:
        # Convert PIL Image to numpy array for OpenCV processing
        img_array = np.array(image)
        
        # Enhance contrast
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGBA2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced_lab = cv2.merge((l, a, b))
        enhanced_rgb = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGBA)
        
        # Convert back to PIL Image
        enhanced_pil = Image.fromarray(enhanced_rgb)
        
        # Sharpen slightly
        enhancer = ImageEnhance.Sharpness(enhanced_pil)
        enhanced_pil = enhancer.enhance(1.2)
        
        return enhanced_pil
    
    except Exception:
        # If enhancement fails, return original
        return image
