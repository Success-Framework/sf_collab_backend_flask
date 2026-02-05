from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import base64
from io import BytesIO
from datetime import datetime
import uuid
import logging

# PDF Libraries
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image
from flask_jwt_extended import jwt_required, get_jwt_identity

# Create blueprint
pdf_bp = Blueprint('pdf', __name__)

# Configuration
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'pdf_documents')
SIGNED_FOLDER = os.path.join(BASE_DIR, 'uploads', 'signed_documents')
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SIGNED_FOLDER, exist_ok=True)

def get_user_upload_folder(user_id):
    """Get user-specific upload folder"""
    folder = os.path.join(UPLOAD_FOLDER, str(user_id))
    os.makedirs(folder, exist_ok=True)
    return folder

def get_user_signed_folder(user_id):
    """Get user-specific signed documents folder"""
    folder = os.path.join(SIGNED_FOLDER, str(user_id))
    os.makedirs(folder, exist_ok=True)
    return folder

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file, max_size=MAX_FILE_SIZE):
    """Validate file size"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= max_size

def process_signature_image(base64_data):
    """Convert base64 signature to PIL Image"""
    try:
        if 'base64,' in base64_data:
            base64_data = base64_data.split('base64,')[1]
        
        image_data = base64.b64decode(base64_data)
        image = Image.open(BytesIO(image_data))
        
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        return image
    except Exception as e:
        logging.error(f'Error processing signature: {str(e)}')
        return None

def create_signature_overlay(signature_image, position, pdf_width, pdf_height):
    """Create a PDF overlay with the signature"""
    packet = BytesIO()
    
    can = canvas.Canvas(packet, pagesize=(pdf_width, pdf_height))
    
    x = position['x']
    y = pdf_height - position['y'] - position['height']
    width = position['width']
    height = position['height']
    
    img_reader = ImageReader(signature_image)
    can.drawImage(img_reader, x, y, width, height, mask='auto', preserveAspectRatio=True)
    
    can.setFont("Helvetica", 8)
    can.drawString(x, y - 10, f"Signed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    can.save()
    packet.seek(0)
    
    return packet

#! HEALTH CHECK
@pdf_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'pdf_signing'
        })
    
    except Exception as e:
        logging.error(f'Error in health check: {str(e)}')
        return jsonify({'error': str(e)}), 500

#! UPLOAD PDF
@pdf_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_pdf():
    """Upload PDF file"""
    try:
        user_id = get_jwt_identity()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF allowed'}), 400
        
        if not validate_file_size(file):
            return jsonify({'error': f'File size exceeds maximum limit of {MAX_FILE_SIZE / (1024*1024)}MB'}), 400
        
        user_upload_folder = get_user_upload_folder(user_id)
        
        original_filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        filename = f"{unique_id}_{original_filename}"
        filepath = os.path.join(user_upload_folder, filename)
        
        file.save(filepath)
        
        with open(filepath, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
            
            first_page = pdf_reader.pages[0]
            width = float(first_page.mediabox.width)
            height = float(first_page.mediabox.height)
        
        return jsonify({
            'success': True,
            'file_id': unique_id,
            'filename': filename,
            'original_filename': original_filename,
            'num_pages': num_pages,
            'page_width': width,
            'page_height': height,
            'message': 'PDF uploaded successfully'
        })
    
    except Exception as e:
        logging.error(f'Error uploading PDF: {str(e)}')
        return jsonify({'error': str(e)}), 500

#! SIGN PDF
@pdf_bp.route('/sign', methods=['POST'])
@jwt_required()
def sign_pdf():
    """Sign the PDF with signature"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        required_fields = ['file_id', 'filename', 'signature', 'position']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        file_id = data['file_id']
        filename = data['filename']
        signature_base64 = data['signature']
        position = data['position']
        
        if not all(k in position for k in ['x', 'y', 'width', 'height', 'page']):
            return jsonify({'error': 'Invalid position data'}), 400
        
        user_upload_folder = get_user_upload_folder(user_id)
        user_signed_folder = get_user_signed_folder(user_id)
        
        original_path = os.path.join(user_upload_folder, filename)
        
        if not os.path.exists(original_path):
            return jsonify({'error': 'Original PDF not found'}), 404
        
        signature_img = process_signature_image(signature_base64)
        if signature_img is None:
            return jsonify({'error': 'Invalid signature image'}), 400
        
        with open(original_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            pdf_writer = PdfWriter()
            
            target_page_num = position['page'] - 1
            
            target_page = pdf_reader.pages[target_page_num]
            page_width = float(target_page.mediabox.width)
            page_height = float(target_page.mediabox.height)
            
            overlay_pdf = create_signature_overlay(
                signature_img, 
                position, 
                page_width, 
                page_height
            )
            
            overlay_reader = PdfReader(overlay_pdf)
            overlay_page = overlay_reader.pages[0]
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                
                if page_num == target_page_num:
                    page.merge_page(overlay_page)
                
                pdf_writer.add_page(page)
            
            signed_filename = f"signed_{file_id}_{data.get('original_filename', 'document.pdf')}"
            signed_path = os.path.join(user_signed_folder, signed_filename)
            
            with open(signed_path, 'wb') as signed_file:
                pdf_writer.write(signed_file)
            
            file_size = os.path.getsize(signed_path)
            
            return jsonify({
                'success': True,
                'signed_filename': signed_filename,
                'file_size': file_size,
                'download_url': f'/api/pdf/download/{signed_filename}',
                'message': 'PDF signed successfully'
            })
    
    except Exception as e:
        logging.error(f'Error signing PDF: {str(e)}')
        return jsonify({'error': str(e)}), 500

#! DOWNLOAD SIGNED PDF
@pdf_bp.route('/download/<filename>', methods=['GET'])
@jwt_required()
def download_signed_pdf(filename):
    """Download signed PDF"""
    try:
        user_id = get_jwt_identity()
        user_signed_folder = get_user_signed_folder(user_id)
        filepath = os.path.join(user_signed_folder, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            filepath,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        logging.error(f'Error downloading PDF: {str(e)}')
        return jsonify({'error': str(e)}), 500

#! LIST SIGNED DOCUMENTS
@pdf_bp.route('/documents', methods=['GET'])
@jwt_required()
def list_signed_documents():
    """List all signed documents for the current user"""
    try:
        user_id = get_jwt_identity()
        user_signed_folder = get_user_signed_folder(user_id)
        documents = []
        
        for filename in os.listdir(user_signed_folder):
            if filename.endswith('.pdf'):
                filepath = os.path.join(user_signed_folder, filename)
                file_stat = os.stat(filepath)
                
                documents.append({
                    'id': filename,
                    'name': filename,
                    'size': file_stat.st_size,
                    'date': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'download_url': f'/api/pdf/download/{filename}'
                })
        
        documents.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'success': True,
            'documents': documents,
            'count': len(documents)
        })
    
    except Exception as e:
        logging.error(f'Error listing documents: {str(e)}')
        return jsonify({'error': str(e)}), 500

#! DELETE DOCUMENT
@pdf_bp.route('/delete/<filename>', methods=['DELETE'])
@jwt_required()
def delete_document(filename):
    """Delete a signed document"""
    try:
        user_id = get_jwt_identity()
        user_signed_folder = get_user_signed_folder(user_id)
        filepath = os.path.join(user_signed_folder, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': 'Document deleted successfully'
        })
    
    except Exception as e:
        logging.error(f'Error deleting document: {str(e)}')
        return jsonify({'error': str(e)}), 500

#! PREVIEW PDF
@pdf_bp.route('/preview/<filename>', methods=['GET'])
@jwt_required()
def preview_pdf(filename):
    """Get PDF preview (first page as image)"""
    try:
        user_id = get_jwt_identity()
        user_upload_folder = get_user_upload_folder(user_id)
        filepath = os.path.join(user_upload_folder, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Preview endpoint - implement with pdf2image for image conversion',
            'preview_available': False
        })
    
    except Exception as e:
        logging.error(f'Error previewing PDF: {str(e)}')
        return jsonify({'error': str(e)}), 500