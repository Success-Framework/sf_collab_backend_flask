# image_editor_routes.py
import os
import io
import base64
import logging
from datetime import datetime
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont
import uuid

# Create blueprint
image_editor_bp = Blueprint('image_editor', __name__, url_prefix='/api/image-editor')

# Configuration
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'edited_images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

# Create upload folder
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file_size):
    return file_size <= MAX_FILE_SIZE

def base64_to_image(base64_data):
    """Convert base64 data to PIL Image"""
    if 'base64,' in base64_data:
        base64_data = base64_data.split('base64,')[1]
    
    image_bytes = base64.b64decode(base64_data)
    return Image.open(io.BytesIO(image_bytes))

def image_to_base64(image, format='PNG'):
    """Convert PIL Image to base64"""
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()

def standard_response(success=True, data=None, error=None, code=200):
    response = jsonify({
        'success': success,
        'data': data,
        'error': error
    })
    return response, code

#! HEALTH CHECK
@image_editor_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return standard_response(True, {
            'status': 'ready',
            'timestamp': datetime.now().isoformat(),
            'upload_folder': UPLOAD_FOLDER,
            'max_file_size': MAX_FILE_SIZE
        })
    except Exception as e:
        logging.error(f'Health check error: {str(e)}')
        return standard_response(False, None, str(e), 500)

#! SAVE IMAGE
@image_editor_bp.route('/save', methods=['POST'])
def save_image():
    """Save the edited image"""
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return standard_response(False, None, 'No image data provided', 400)
        
        image_data = data['image']
        filename = data.get('filename', f'edited_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        
        # Validate filename
        if not filename or len(filename) > 255:
            filename = f'edited_{uuid.uuid4().hex[:8]}.png'
        
        # Convert base64 to image
        img = base64_to_image(image_data)
        
        # Save to file
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        img.save(filepath, format='PNG')
        
        # Get file info
        file_size = os.path.getsize(filepath)
        
        return standard_response(True, {
            'message': 'Image saved successfully',
            'filename': filename,
            'filepath': filepath,
            'size': file_size,
            'dimensions': f'{img.width}x{img.height}',
            'format': img.format or 'PNG',
            'download_url': f'/api/image-editor/download/{filename}'
        })
    
    except Exception as e:
        logging.error(f'Error saving image: {str(e)}')
        return standard_response(False, None, str(e), 500)

#! PROCESS IMAGE
@image_editor_bp.route('/process', methods=['POST'])
def process_image():
    """Apply image processing operations"""
    try:
        data = request.get_json()
        
        if not data or 'image' not in data or 'operation' not in data:
            return standard_response(False, None, 'Missing image data or operation', 400)
        
        image_data = data['image']
        operation = data['operation']
        params = data.get('params', {})
        
        # Convert base64 to image
        img = base64_to_image(image_data)
        
        # Apply operation
        if operation == 'brightness':
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(params.get('value', 1.0))
            
        elif operation == 'contrast':
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(params.get('value', 1.0))
            
        elif operation == 'saturation':
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(params.get('value', 1.0))
            
        elif operation == 'sharpness':
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(params.get('value', 1.0))
            
        elif operation == 'blur':
            radius = params.get('radius', 2)
            img = img.filter(ImageFilter.GaussianBlur(radius=radius))
            
        elif operation == 'sharpen':
            img = img.filter(ImageFilter.SHARPEN)
            
        elif operation == 'emboss':
            img = img.filter(ImageFilter.EMBOSS)
            
        elif operation == 'contour':
            img = img.filter(ImageFilter.CONTOUR)
            
        elif operation == 'edge_enhance':
            img = img.filter(ImageFilter.EDGE_ENHANCE)
            
        elif operation == 'find_edges':
            img = img.filter(ImageFilter.FIND_EDGES)
            
        elif operation == 'grayscale':
            img = ImageOps.grayscale(img)
            
        elif operation == 'invert':
            img = ImageOps.invert(img)
            
        elif operation == 'solarize':
            threshold = params.get('threshold', 128)
            img = ImageOps.solarize(img, threshold=threshold)
            
        elif operation == 'resize':
            width = params.get('width', img.width)
            height = params.get('height', img.height)
            maintain_aspect = params.get('maintain_aspect', True)
            
            if maintain_aspect:
                # Calculate new dimensions while maintaining aspect ratio
                ratio = min(width / img.width, height / img.height)
                new_width = int(img.width * ratio)
                new_height = int(img.height * ratio)
                img = img.resize((new_width, new_height), Image.LANCZOS)
            else:
                img = img.resize((width, height), Image.LANCZOS)
                
        elif operation == 'crop':
            left = params.get('left', 0)
            top = params.get('top', 0)
            right = params.get('right', img.width)
            bottom = params.get('bottom', img.height)
            img = img.crop((left, top, right, bottom))
            
        elif operation == 'rotate':
            angle = params.get('angle', 0)
            expand = params.get('expand', True)
            img = img.rotate(angle, expand=expand)
            
        elif operation == 'flip_horizontal':
            img = ImageOps.mirror(img)
            
        elif operation == 'flip_vertical':
            img = ImageOps.flip(img)
            
        elif operation == 'add_text':
            text = params.get('text', '')
            x = params.get('x', 10)
            y = params.get('y', 10)
            font_size = params.get('font_size', 20)
            color = params.get('color', '#000000')
            alpha = params.get('alpha', 255)
            
            if text:
                # Create drawing context
                draw = ImageDraw.Draw(img)
                
                # Try to load font
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                
                # Convert hex color to RGB
                if color.startswith('#'):
                    color = color.lstrip('#')
                    rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
                else:
                    rgb = (0, 0, 0)
                
                # Add alpha if specified
                if alpha < 255:
                    rgb = rgb + (alpha,)
                
                # Draw text
                draw.text((x, y), text, fill=rgb, font=font)
        
        else:
            return standard_response(False, None, f'Unknown operation: {operation}', 400)
        
        # Convert back to base64
        processed_image = image_to_base64(img)
        
        return standard_response(True, {
            'image': f'data:image/png;base64,{processed_image}',
            'dimensions': f'{img.width}x{img.height}',
            'format': 'PNG',
            'operation': operation
        })
    
    except Exception as e:
        logging.error(f'Error processing image: {str(e)}')
        return standard_response(False, None, str(e), 500)

#! COMPRESS IMAGE
@image_editor_bp.route('/compress', methods=['POST'])
def compress_image():
    """Compress image to reduce file size"""
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return standard_response(False, None, 'No image data provided', 400)
        
        image_data = data['image']
        quality = data.get('quality', 85)
        format = data.get('format', 'JPEG')
        
        if quality < 1 or quality > 100:
            return standard_response(False, None, 'Quality must be between 1 and 100', 400)
        
        # Convert base64 to image
        img = base64_to_image(image_data)
        
        # Convert to RGB if necessary (for JPEG)
        if format.upper() == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Get original size
        original_buffer = io.BytesIO()
        img.save(original_buffer, format='PNG', quality=100)
        original_size = len(original_buffer.getvalue())
        
        # Compress image
        buffer = io.BytesIO()
        
        if format.upper() == 'JPEG':
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
        elif format.upper() == 'WEBP':
            img.save(buffer, format='WEBP', quality=quality, method=6)
        else:
            img.save(buffer, format='PNG', optimize=True)
        
        buffer.seek(0)
        compressed_size = len(buffer.getvalue())
        compressed_image = base64.b64encode(buffer.getvalue()).decode()
        
        # Calculate savings
        savings = ((original_size - compressed_size) / original_size) * 100
        
        return standard_response(True, {
            'image': f'data:image/{format.lower()};base64,{compressed_image}',
            'original_size': original_size,
            'compressed_size': compressed_size,
            'savings_percent': round(savings, 2),
            'quality': quality,
            'format': format.upper()
        })
    
    except Exception as e:
        logging.error(f'Error compressing image: {str(e)}')
        return standard_response(False, None, str(e), 500)

#! BATCH PROCESS
@image_editor_bp.route('/batch-process', methods=['POST'])
def batch_process():
    """Apply multiple operations in sequence"""
    try:
        data = request.get_json()
        
        if not data or 'image' not in data or 'operations' not in data:
            return standard_response(False, None, 'Missing image data or operations', 400)
        
        image_data = data['image']
        operations = data['operations']
        
        if not isinstance(operations, list):
            return standard_response(False, None, 'Operations must be a list', 400)
        
        # Convert base64 to image
        img = base64_to_image(image_data)
        
        applied_operations = []
        
        # Apply each operation in sequence
        for op in operations:
            operation = op.get('operation')
            params = op.get('params', {})
            
            if not operation:
                continue
            
            # Apply operation (reuse logic from /process endpoint)
            # For brevity, you could refactor this to call the same processing function
            # For now, we'll handle the most common operations
            
            if operation == 'brightness':
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(params.get('value', 1.0))
                
            elif operation == 'contrast':
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(params.get('value', 1.0))
                
            elif operation == 'grayscale':
                img = ImageOps.grayscale(img)
                
            elif operation == 'blur':
                radius = params.get('radius', 2)
                img = img.filter(ImageFilter.GaussianBlur(radius=radius))
                
            elif operation == 'resize':
                width = params.get('width', img.width)
                height = params.get('height', img.height)
                img = img.resize((width, height), Image.LANCZOS)
            
            applied_operations.append(operation)
        
        # Convert back to base64
        processed_image = image_to_base64(img)
        
        return standard_response(True, {
            'image': f'data:image/png;base64,{processed_image}',
            'dimensions': f'{img.width}x{img.height}',
            'applied_operations': applied_operations
        })
    
    except Exception as e:
        logging.error(f'Error in batch processing: {str(e)}')
        return standard_response(False, None, str(e), 500)

#! DOWNLOAD IMAGE
@image_editor_bp.route('/download/<filename>', methods=['GET'])
def download_image(filename):
    """Download saved image"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return standard_response(False, None, 'File not found', 404)
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='image/png'
        )
    
    except Exception as e:
        logging.error(f'Error downloading image: {str(e)}')
        return standard_response(False, None, str(e), 500)

#! LIST IMAGES
@image_editor_bp.route('/images', methods=['GET'])
def list_images():
    """List all saved images"""
    try:
        images = []
        
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                stat = os.stat(filepath)
                
                # Get image dimensions
                try:
                    with Image.open(filepath) as img:
                        width, height = img.size
                        format = img.format or 'Unknown'
                except:
                    width, height = 0, 0
                    format = 'Unknown'
                
                images.append({
                    'filename': filename,
                    'path': filepath,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'dimensions': f'{width}x{height}',
                    'format': format,
                    'download_url': f'/api/image-editor/download/{filename}'
                })
        
        # Sort by modification time (newest first)
        images.sort(key=lambda x: x['modified'], reverse=True)
        
        return standard_response(True, {
            'images': images,
            'count': len(images)
        })
    
    except Exception as e:
        logging.error(f'Error listing images: {str(e)}')
        return standard_response(False, None, str(e), 500)