from flask import Blueprint, request, jsonify, send_file
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import io
import numpy as np
import cv2
import os

# Create blueprint
anime_converter_bp = Blueprint('anime_converter', __name__, url_prefix='/api/anime-converter')

# Check if CUDA is available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Image preprocessing
transform = transforms.Compose([
    transforms.Resize((512, 512)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

# Simple style transfer model (you can replace with a real anime GAN)
class SimpleAnimeConverter(nn.Module):
    def __init__(self):
        super(SimpleAnimeConverter, self).__init__()
        # Simplified model for demonstration
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 3, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        x = torch.tanh(self.conv3(x))
        return x

# Initialize model
model = SimpleAnimeConverter().to(device)

@anime_converter_bp.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'anime-converter',
        'device': str(device)
    }), 200

@anime_converter_bp.route('/convert', methods=['POST'])
def convert_to_anime():
    """
    Convert photo to anime style
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
        
        # Open image
        img = Image.open(file.stream).convert('RGB')
        
        # Apply anime-style effects (simplified version)
        # In production, you'd use a proper anime GAN model
        
        # Method 1: Cartoon effect using OpenCV
        cartoon_img = apply_cartoon_effect(img)
        
        # Save to bytes
        img_io = io.BytesIO()
        cartoon_img.save(img_io, 'PNG', quality=95)
        img_io.seek(0)
        
        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'anime_{file.filename}.png'
        )
        
    except Exception as e:
        print(f"Error converting to anime: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@anime_converter_bp.route('/convert-advanced', methods=['POST'])
def convert_to_anime_advanced():
    """
    Advanced anime conversion with different styles
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        style = request.form.get('style', 'standard')  # standard, shonen, shojo, chibi
        
        img = Image.open(file.stream).convert('RGB')
        
        # Apply different styles based on selection
        if style == 'shonen':
            result = apply_shonen_style(img)
        elif style == 'shojo':
            result = apply_shojo_style(img)
        elif style == 'chibi':
            result = apply_chibi_style(img)
        else:
            result = apply_standard_anime_style(img)
        
        img_io = io.BytesIO()
        result.save(img_io, 'PNG', quality=95)
        img_io.seek(0)
        
        return send_file(
            img_io,
            mimetype='image/png',
            download_name=f'anime_{style}_{file.filename}.png'
        )
        
    except Exception as e:
        print(f"Error in advanced conversion: {e}")
        return jsonify({'error': str(e)}), 500

def apply_cartoon_effect(pil_image):
    """Apply cartoon effect to image"""
    # Convert PIL to OpenCV
    img = np.array(pil_image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    # Apply cartoon effect
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255,
                                  cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 9)
    
    # Color quantization
    data = np.float32(img).reshape((-1, 3))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, labels, centers = cv2.kmeans(data, 8, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    centers = np.uint8(centers)
    quantized = centers[labels.flatten()]
    quantized = quantized.reshape(img.shape)
    
    # Apply bilateral filter
    filtered = cv2.bilateralFilter(quantized, 9, 300, 300)
    
    # Combine edges with color
    cartoon = cv2.bitwise_and(filtered, filtered, mask=edges)
    
    # Convert back to PIL
    cartoon = cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB)
    return Image.fromarray(cartoon)

def apply_standard_anime_style(pil_image):
    """Apply standard anime style"""
    img = np.array(pil_image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    # Edge enhancement
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    
    # Color simplification
    data = np.float32(img).reshape((-1, 3))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, labels, centers = cv2.kmeans(data, 6, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    centers = np.uint8(centers)
    quantized = centers[labels.flatten()]
    quantized = quantized.reshape(img.shape)
    
    # Smooth colors
    smoothed = cv2.bilateralFilter(quantized, 9, 75, 75)
    
    # Add anime-like saturation
    hsv = cv2.cvtColor(smoothed, cv2.COLOR_BGR2HSV)
    hsv[:, :, 1] = hsv[:, :, 1] * 1.2  # Increase saturation
    hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
    saturated = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    # Convert back
    result = cv2.cvtColor(saturated, cv2.COLOR_BGR2RGB)
    return Image.fromarray(result)

def apply_shonen_style(pil_image):
    """Apply shonen anime style (bold, action-oriented)"""
    img = apply_standard_anime_style(pil_image)
    img_array = np.array(img)
    
    # Increase contrast for bold look
    img_array = cv2.convertScaleAbs(img_array, alpha=1.2, beta=0)
    
    return Image.fromarray(img_array)

def apply_shojo_style(pil_image):
    """Apply shojo anime style (soft, romantic)"""
    img = apply_standard_anime_style(pil_image)
    img_array = np.array(img)
    
    # Soft glow effect
    blur = cv2.GaussianBlur(img_array, (0, 0), 3)
    img_array = cv2.addWeighted(img_array, 0.7, blur, 0.3, 0)
    
    # Soft pink tint
    img_array = img_array.astype(np.float32)
    img_array[:, :, 0] *= 0.95  # Reduce blue
    img_array[:, :, 2] *= 1.05  # Increase red
    img_array = np.clip(img_array, 0, 255).astype(np.uint8)
    
    return Image.fromarray(img_array)

def apply_chibi_style(pil_image):
    """Apply chibi style (cute, big head)"""
    img = np.array(pil_image)
    
    # Resize for chibi proportions
    height, width = img.shape[:2]
    new_height = int(height * 0.8)  # Shorter body
    new_width = int(width * 1.1)    # Wider head
    
    # Resize head area more
    head_roi = img[:height//2, :]
    head_resized = cv2.resize(head_roi, (new_width, new_height//2))
    
    # Resize body less
    body_roi = img[height//2:, :]
    body_resized = cv2.resize(body_roi, (width, new_height//2))
    
    # Combine
    chibi = np.vstack([head_resized, body_resized])
    
    # Apply anime style
    chibi_pil = Image.fromarray(chibi)
    anime_chibi = apply_standard_anime_style(chibi_pil)
    
    return anime_chibi

@anime_converter_bp.route('/styles', methods=['GET'])
def get_styles():
    """Get available anime styles"""
    return jsonify({
        'success': True,
        'styles': [
            {'id': 'standard', 'name': 'Standard Anime', 'description': 'Classic anime style'},
            {'id': 'shonen', 'name': 'Shonen Style', 'description': 'Bold, action-oriented'},
            {'id': 'shojo', 'name': 'Shojo Style', 'description': 'Soft, romantic style'},
            {'id': 'chibi', 'name': 'Chibi Style', 'description': 'Cute, big head style'}
        ]
    }), 200