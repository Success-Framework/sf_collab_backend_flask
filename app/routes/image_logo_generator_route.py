import os
import torch
import base64
from io import BytesIO
from flask import Blueprint, request, jsonify
from PIL import Image
import logging
from flask_jwt_extended import jwt_required
import gc
import hashlib
import json
import time
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint for image generation routes
image_generation_bp = Blueprint('image_generation', __name__, url_prefix='/api/generation')

# Configuration - SIMPLIFIED: Let HuggingFace handle caching
MODEL_CONFIG = {
    'text_generation': 'Qwen/Qwen2.5-1.5B-Instruct',
    'image_generation': 'stabilityai/stable-diffusion-xl-base-1.0',
}

# Global variables
text_model = None
text_tokenizer = None
image_pipeline = None
models_initialized = False
device = None
init_lock = False

# FORCE OFFLINE MODE TO PREVENT NETWORK ERRORS
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['DIFFUSERS_OFFLINE'] = '1'

def get_device():
    """Determine the best available device"""
    global device
    if device is None:
        if torch.cuda.is_available():
            device = "cuda"
            logger.info(f"✅ Using CUDA device: {torch.cuda.get_device_name(0)}")
        elif torch.backends.mps.is_available() and torch.backends.mps.is_built():
            device = "mps"
            logger.info("✅ Using Apple MPS")
        else:
            device = "cpu"
            logger.info("⚠️  Using CPU (slow)")
    return device

def check_model_cache():
    """Check if models exist in ANY cache location"""
    # HuggingFace cache locations
    possible_cache_locations = [
        './model_cache',
        os.path.expanduser('~/.cache/huggingface/hub'),
        os.path.expanduser('~/.huggingface/hub'),
        '/tmp/huggingface/hub',
    ]
    
    found_models = []
    
    for cache_dir in possible_cache_locations:
        if os.path.exists(cache_dir):
            logger.info(f"🔍 Checking cache: {cache_dir}")
            
            for model_type, model_name in MODEL_CONFIG.items():
                # Convert model name to cache format
                cache_model_name = f"models--{model_name.replace('/', '--')}"
                model_cache_path = os.path.join(cache_dir, cache_model_name)
                
                if os.path.exists(model_cache_path):
                    # Check for snapshots
                    snapshots_path = os.path.join(model_cache_path, 'snapshots')
                    if os.path.exists(snapshots_path):
                        snapshots = os.listdir(snapshots_path)
                        if snapshots:
                            found_models.append(model_name)
                            logger.info(f"✅ Found {model_type} in {cache_dir}: {model_name}")
                        else:
                            logger.warning(f"⚠️  No snapshots in {cache_dir} for {model_name}")
                    else:
                        logger.warning(f"⚠️  No snapshots folder in {cache_dir} for {model_name}")
                else:
                    logger.warning(f"❌ Model not in {cache_dir}: {model_name}")
    
    # Log what we found
    logger.info(f"📊 Found models: {found_models}")
    logger.info(f"📊 Required models: {list(MODEL_CONFIG.values())}")
    
    return len(found_models) == len(MODEL_CONFIG)

def initialize_models():
    """Initialize models - FIXED CACHE ISSUE"""
    global text_model, text_tokenizer, image_pipeline, models_initialized, init_lock
    
    if models_initialized:
        return True
    
    if init_lock:
        logger.info("⏳ Another initialization in progress, waiting...")
        while init_lock:
            time.sleep(1)
        return models_initialized
    
    init_lock = True
    
    try:
        logger.info("="*60)
        logger.info("🚀 STARTING MODEL INITIALIZATION...")
        logger.info("="*60)
        
        # Get device
        current_device = get_device()
        dtype = torch.float16 if current_device == "cuda" else torch.float32
        
        # Check cache
        cache_ready = check_model_cache()
        if not cache_ready:
            logger.error("❌ Models not fully cached. Please check if both models are downloaded.")
            logger.error("📝 To download models, run: python -c \"from transformers import AutoModelForCausalLM; from diffusers import DiffusionPipeline; import torch; AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-1.5B-Instruct', torch_dtype=torch.float32); DiffusionPipeline.from_pretrained('stabilityai/stable-diffusion-xl-base-1.0', torch_dtype=torch.float32)\"")
            raise Exception("Models not cached. Please download them first.")
        
        # 1. Initialize TEXT model
        logger.info("📦 LOADING TEXT GENERATION MODEL...")
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        try:
            # Force local files only
            text_tokenizer = AutoTokenizer.from_pretrained(
                MODEL_CONFIG['text_generation'],
                trust_remote_code=True,
                use_fast=True,
                local_files_only=True  # FORCE LOCAL ONLY
            )
            
            # Set padding token
            if text_tokenizer.pad_token is None:
                text_tokenizer.pad_token = text_tokenizer.eos_token
            
            text_model = AutoModelForCausalLM.from_pretrained(
                MODEL_CONFIG['text_generation'],
                torch_dtype=dtype,  # Keep torch_dtype for compatibility
                trust_remote_code=True,
                low_cpu_mem_usage=True,
                device_map="auto" if current_device == "cuda" else None,
                local_files_only=True  # FORCE LOCAL ONLY
            )
            
            if current_device == "cuda":
                text_model = text_model.to(current_device)
            elif current_device == "mps":
                text_model = text_model.to("mps")
            else:
                text_model = text_model.to("cpu")
            
            text_model.eval()
            logger.info(f"✅ TEXT MODEL LOADED on {current_device}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load text model: {str(e)}")
            raise
        
        # 2. Initialize IMAGE model
        logger.info("📦 LOADING IMAGE GENERATION MODEL...")
        
        try:
            # Try to load with diffusers - FORCE LOCAL
            from diffusers import DiffusionPipeline
            
            image_pipeline = DiffusionPipeline.from_pretrained(
                MODEL_CONFIG['image_generation'],
                torch_dtype=dtype,
                use_safetensors=True,
                variant="fp16" if current_device == "cuda" else None,
                low_cpu_mem_usage=True,
                safety_checker=None,
                local_files_only=True  # FORCE LOCAL ONLY
            )
            
            # Move to appropriate device
            if current_device == "cuda":
                image_pipeline = image_pipeline.to(current_device)
                try:
                    image_pipeline.enable_xformers_memory_efficient_attention()
                    logger.info("✅ Enabled xformers memory efficient attention")
                except:
                    logger.info("ℹ️  xformers not available, using standard attention")
            elif current_device == "mps":
                image_pipeline = image_pipeline.to("mps")
            else:
                image_pipeline = image_pipeline.to("cpu")
            
            logger.info(f"✅ IMAGE MODEL LOADED on {current_device}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load image model with DiffusionPipeline: {str(e)}")
            
            # Try StableDiffusionXLPipeline
            try:
                logger.info("🔄 Trying StableDiffusionXLPipeline...")
                from diffusers import StableDiffusionXLPipeline
                
                image_pipeline = StableDiffusionXLPipeline.from_pretrained(
                    MODEL_CONFIG['image_generation'],
                    torch_dtype=dtype,
                    use_safetensors=True,
                    low_cpu_mem_usage=True,
                    local_files_only=True
                )
                
                if current_device == "cuda":
                    image_pipeline = image_pipeline.to(current_device)
                else:
                    image_pipeline = image_pipeline.to("cpu")
                    
                logger.info(f"✅ IMAGE MODEL LOADED (StableDiffusionXLPipeline) on {current_device}")
            except Exception as e2:
                logger.error(f"❌ Failed with StableDiffusionXLPipeline: {str(e2)}")
                
                # Try regular StableDiffusionPipeline
                try:
                    logger.info("🔄 Trying StableDiffusionPipeline...")
                    from diffusers import StableDiffusionPipeline
                    
                    image_pipeline = StableDiffusionPipeline.from_pretrained(
                        MODEL_CONFIG['image_generation'],
                        torch_dtype=dtype,
                        low_cpu_mem_usage=True,
                        safety_checker=None,
                        local_files_only=True
                    )
                    
                    if current_device == "cuda":
                        image_pipeline = image_pipeline.to(current_device)
                    else:
                        image_pipeline = image_pipeline.to("cpu")
                        
                    logger.info(f"✅ IMAGE MODEL LOADED (StableDiffusionPipeline) on {current_device}")
                except Exception as e3:
                    logger.error(f"❌ All loading methods failed: {str(e3)}")
                    
                    # Check what's actually in cache
                    logger.error("🔍 Checking what's in model cache...")
                    cache_path = './model_cache'
                    if os.path.exists(cache_path):
                        for item in os.listdir(cache_path):
                            if 'stable' in item.lower() or 'diffusion' in item.lower():
                                logger.error(f"📁 Found in cache: {item}")
                                item_path = os.path.join(cache_path, item)
                                if os.path.isdir(item_path):
                                    for subitem in os.listdir(item_path):
                                        logger.error(f"   └── {subitem}")
                    
                    raise e
        
        # Memory cleanup
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        models_initialized = True
        logger.info("="*60)
        logger.info("✅ ALL MODELS INITIALIZED SUCCESSFULLY!")
        logger.info("="*60)
        return True
        
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR initializing models: {str(e)}", exc_info=True)
        models_initialized = False
        
        # Clean up on error
        text_model = None
        text_tokenizer = None
        image_pipeline = None
        gc.collect()
        
        raise e
    finally:
        init_lock = False

def ensure_models_loaded():
    """Ensure models are loaded with retry logic"""
    if not models_initialized:
        max_retries = 2
        for attempt in range(max_retries):
            try:
                initialize_models()
                return
            except Exception as e:
                logger.error(f"⚠️  Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)
                gc.collect()

def image_to_base64(pil_image, max_size=768, quality=90):
    """Convert PIL image to optimized base64 string"""
    try:
        # Resize if too large
        if max(pil_image.width, pil_image.height) > max_size:
            ratio = max_size / max(pil_image.width, pil_image.height)
            new_width = int(pil_image.width * ratio)
            new_height = int(pil_image.height * ratio)
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to RGB if needed
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        buffered = BytesIO()
        pil_image.save(buffered, format="JPEG", quality=quality, optimize=True)
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        size_kb = len(img_str) * 3 / 4 / 1024
        logger.debug(f"Generated image size: ~{size_kb:.1f} KB")
        
        return img_str
    except Exception as e:
        logger.error(f"❌ Error converting image to base64: {str(e)}")
        return None

def generate_text(prompt, max_length=150, temperature=0.7):
    """Generate text using Qwen model"""
    global text_model, text_tokenizer
    
    ensure_models_loaded()
    
    # Format prompt for Qwen 2.5
    formatted_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
    
    try:
        inputs = text_tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
        
        current_device = get_device()
        inputs = {k: v.to(current_device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = text_model.generate(
                **inputs,
                max_new_tokens=max_length,
                do_sample=True,
                temperature=temperature,
                top_p=0.9,
                top_k=50,
                pad_token_id=text_tokenizer.pad_token_id,
                eos_token_id=text_tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        response = text_tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the assistant's response
        if '<|im_start|>assistant' in response:
            response = response.split('<|im_start|>assistant')[-1]
        if '<|im_end|>' in response:
            response = response.split('<|im_end|>')[0]
        
        # Clean up
        response = response.strip()
        response = response.replace('<|im_start|>', '').replace('<|im_end|>', '')
        
        logger.info(f"📝 Generated text length: {len(response)} chars")
        return response
        
    except Exception as e:
        logger.error(f"❌ Text generation failed: {str(e)}")
        return f"Error generating text: {str(e)}"

def generate_image(prompt, fast_mode=True, negative_prompt=None, size=512):
    """Generate image with better defaults"""
    global image_pipeline
    
    ensure_models_loaded()
    
    # Default negative prompt for better results
    if negative_prompt is None:
        negative_prompt = "blurry, low quality, distorted, ugly, bad anatomy, watermark, signature, text"
    
    steps = 20 if fast_mode else 30
    current_device = get_device()
    
    logger.info(f"🎨 Generating image: '{prompt[:50]}...' (steps: {steps}, size: {size})")
    
    try:
        with torch.no_grad():
            # Set generator for reproducibility
            seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16) % 2**32
            
            if current_device == "cuda":
                generator = torch.Generator(device="cuda").manual_seed(seed)
            elif current_device == "mps":
                generator = torch.Generator(device="mps").manual_seed(seed)
            else:
                generator = torch.Generator().manual_seed(seed)
            
            # Generate image
            image = image_pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=steps,
                guidance_scale=7.5,
                width=size,
                height=size,
                generator=generator
            ).images[0]
        
        # Memory cleanup
        gc.collect()
        if current_device == "cuda":
            torch.cuda.empty_cache()
        
        logger.info("✅ Image generated successfully")
        return image_to_base64(image)
        
    except Exception as e:
        logger.error(f"❌ Image generation failed: {str(e)}")
        
        # Try with simpler settings if failed
        if "memory" in str(e).lower() or "cuda" in str(e).lower() or "cpu" in str(e).lower():
            logger.info("🔄 Trying with lower settings due to memory error...")
            try:
                with torch.no_grad():
                    image = image_pipeline(
                        prompt=prompt,
                        num_inference_steps=15,
                        guidance_scale=7.0,
                        width=384,
                        height=384,
                    ).images[0]
                return image_to_base64(image)
            except Exception as e2:
                logger.error(f"❌ Retry also failed: {str(e2)}")
        
        return None

def create_logo_specific_prompt(company_name, subtitle, industry, style_preference, color_palette, additional_notes):
    """Create a highly specific prompt optimized for logo generation"""
    logo_prompt = f"Professional logo design for {company_name}, a {industry} company. "
    logo_prompt += f"Tagline: '{subtitle}'. " if subtitle else ""
    logo_prompt += f"Style: {style_preference}. "
    logo_prompt += f"Colors: {color_palette}. "
    logo_prompt += f"Additional requirements: {additional_notes}. " if additional_notes else ""
    logo_prompt += "Clean, modern, professional logo, vector style, scalable, minimalist, high quality, no text, no watermark"
    
    return logo_prompt.strip()

@image_generation_bp.route('/generate-logo', methods=['POST'])
@jwt_required()
def generate_logo():
    """Specialized endpoint for startup logo generation with structured inputs"""
    try:
        # Initialize models on first request
        if not models_initialized:
            logger.info("🔄 First request - initializing models...")
            initialize_models()
        
        data = request.get_json()
        
        company_name = data.get('company_name', '').strip()
        subtitle = data.get('subtitle', '').strip()
        industry = data.get('industry', 'Technology')
        style_preference = data.get('style_preference', 'Modern and Minimalist')
        color_palette = data.get('color_palette', 'Blue and White')
        additional_notes = data.get('additional_notes', '')
        skip_description = data.get('skip_description', True)

        if not company_name:
            return jsonify({
                'success': False,
                'error': 'Company name is required for logo generation'
            }), 400

        logo_prompt = create_logo_specific_prompt(
            company_name=company_name,
            subtitle=subtitle,
            industry=industry,
            style_preference=style_preference,
            color_palette=color_palette,
            additional_notes=additional_notes
        )

        logo_description = ""
        if not skip_description:
            description_prompt = f"Describe a professional logo for {company_name} ({industry}) in the style of {style_preference} using colors {color_palette}"
            logo_description = generate_text(description_prompt, max_length=100)
        
        logo_image_b64 = generate_image(logo_prompt, fast_mode=True, size=512)

        if logo_image_b64 is None:
            return jsonify({
                'success': False,
                'error': 'Failed to generate image'
            }), 500

        logger.info(f"✅ Logo generated for: {company_name}")
        
        return jsonify({
            'success': True,
            'company_name': company_name,
            'subtitle': subtitle,
            'logo_description': logo_description,
            'generated_image': logo_image_b64,
            'prompt_used': logo_prompt,
            'image_format': 'jpeg_base64'
        })

    except Exception as e:
        logger.error(f"❌ Logo generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@image_generation_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate():
    """General purpose text-to-text and text-to-image generation"""
    try:
        if not models_initialized:
            initialize_models()
        
        # Get JSON data
        data = request.get_json()
        
        text = data.get('text', '').strip()
        generate_image_flag = data.get('generate_image', False)

        if not text:
            return jsonify({
                'success': False,
                'error': 'Text prompt is required'
            }), 400

        response_data = {
            'success': True,
            'answer': '',
            'generated_image': None
        }

        # Generate text response
        if text:
            response_data['answer'] = generate_text(text, max_length=200)

        # Generate image if requested or if text suggests image
        image_keywords = ['logo', 'design', 'draw', 'create image', 'generate image', 'picture', 'illustration', 'photo', 'painting', 'art', 'graphic']
        if generate_image_flag or any(keyword in text.lower() for keyword in image_keywords):
            try:
                response_data['generated_image'] = generate_image(text, fast_mode=True)
            except Exception as img_error:
                logger.warning(f"⚠️  Image generation failed: {img_error}")
                response_data['image_error'] = str(img_error)

        logger.info("✅ Generation completed")
        
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"❌ Generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@image_generation_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    # Check various cache locations
    cache_locations = [
        './model_cache',
        os.path.expanduser('~/.cache/huggingface/hub'),
        os.path.expanduser('~/.huggingface/hub'),
    ]
    
    cache_info_list = []
    
    for cache_dir in cache_locations:
        if os.path.exists(cache_dir):
            size = 0
            file_count = 0
            for dirpath, dirnames, filenames in os.walk(cache_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        try:
                            size += os.path.getsize(filepath)
                            file_count += 1
                        except:
                            pass
            
            cache_info_list.append({
                'location': cache_dir,
                'exists': True,
                'size_gb': round(size / (1024**3), 2),
                'size_mb': round(size / (1024 * 1024), 2),
                'file_count': file_count
            })
    
    device_info = {
        'cuda_available': torch.cuda.is_available(),
        'cuda_device_count': torch.cuda.device_count() if torch.cuda.is_available() else 0,
        'mps_available': torch.backends.mps.is_available() and torch.backends.mps.is_built(),
        'device': get_device()
    }
    
    if torch.cuda.is_available():
        device_info['cuda_device_name'] = torch.cuda.get_device_name(0)
    
    return jsonify({
        'status': 'healthy' if models_initialized else 'initializing',
        'models_initialized': models_initialized,
        'text_model_loaded': text_model is not None,
        'image_model_loaded': image_pipeline is not None,
        'device': device_info,
        'cache_locations': cache_info_list,
        'timestamp': time.time()
    })

@image_generation_bp.route('/initialize-models', methods=['POST'])
@jwt_required()
def manual_initialize():
    """Manually initialize models endpoint"""
    try:
        if models_initialized:
            return jsonify({
                'success': True,
                'message': 'Models already initialized',
                'text_model': text_model is not None,
                'image_model': image_pipeline is not None,
                'device': get_device()
            })
        
        initialize_models()
        
        return jsonify({
            'success': True,
            'message': 'Models initialized successfully',
            'text_model': text_model is not None,
            'image_model': image_pipeline is not None,
            'device': get_device()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': str(e.__traceback__) if hasattr(e, '__traceback__') else None
        }), 500

@image_generation_bp.route('/clear-cache', methods=['POST'])
@jwt_required()
def clear_cache():
    """Clear model cache (use with caution)"""
    try:
        cache_dir = './model_cache'
        
        if os.path.exists(cache_dir):
            import shutil
            shutil.rmtree(cache_dir)
            os.makedirs(cache_dir, exist_ok=True)
            
            # Reset models
            global text_model, text_tokenizer, image_pipeline, models_initialized
            text_model = None
            text_tokenizer = None
            image_pipeline = None
            models_initialized = False
            
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            return jsonify({
                'success': True,
                'message': 'Cache cleared and models unloaded'
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Cache directory does not exist'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@image_generation_bp.route('/cache-info', methods=['GET'])
def cache_info():
    """Get detailed cache information"""
    cache_locations = [
        './model_cache',
        os.path.expanduser('~/.cache/huggingface/hub'),
        os.path.expanduser('~/.huggingface/hub'),
    ]
    
    all_models_info = []
    
    for cache_dir in cache_locations:
        if not os.path.exists(cache_dir):
            continue
            
        models_info = []
        total_size = 0
        
        for item in os.listdir(cache_dir):
            if item.startswith('models--'):
                model_name = item.replace('models--', '').replace('--', '/')
                model_path = os.path.join(cache_dir, item)
                
                size = 0
                snapshot_count = 0
                if os.path.exists(os.path.join(model_path, 'snapshots')):
                    snapshots_path = os.path.join(model_path, 'snapshots')
                    if os.path.exists(snapshots_path):
                        snapshot_dirs = os.listdir(snapshots_path)
                        snapshot_count = len(snapshot_dirs)
                        
                        # Calculate size
                        for root, dirs, files in os.walk(model_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                if os.path.exists(file_path):
                                    try:
                                        size += os.path.getsize(file_path)
                                    except:
                                        pass
                
                total_size += size
                
                models_info.append({
                    'name': model_name,
                    'cached': snapshot_count > 0,
                    'snapshots': snapshot_count,
                    'size_mb': round(size / (1024 * 1024), 2),
                    'path': model_path
                })
        
        if models_info:
            all_models_info.append({
                'cache_location': cache_dir,
                'total_size_gb': round(total_size / (1024**3), 2),
                'models': models_info
            })
    
    return jsonify({
        'success': True,
        'caches': all_models_info if all_models_info else [{'message': 'No cache directories found'}]
    })

@image_generation_bp.route('/test-text', methods=['POST'])
@jwt_required()
def test_text():
    """Test text generation only"""
    try:
        ensure_models_loaded()
        
        data = request.get_json()
        prompt = data.get('prompt', 'Hello, how are you?')
        
        response = generate_text(prompt, max_length=100)
        
        return jsonify({
            'success': True,
            'prompt': prompt,
            'response': response,
            'model': MODEL_CONFIG['text_generation']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@image_generation_bp.route('/test-image', methods=['POST'])
@jwt_required()
def test_image():
    """Test image generation only"""
    try:
        ensure_models_loaded()
        
        data = request.get_json()
        prompt = data.get('prompt', 'A beautiful sunset over mountains')
        
        image_b64 = generate_image(prompt, fast_mode=True)
        
        if image_b64:
            return jsonify({
                'success': True,
                'prompt': prompt,
                'image_b64_length': len(image_b64),
                'model': MODEL_CONFIG['image_generation']
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate image'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Fix for the seed generator issue
def get_seed_from_prompt(prompt):
    """Generate consistent seed from prompt"""
    return int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16) % 2**32