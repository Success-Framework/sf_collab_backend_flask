import torch
from flask import Blueprint, request, jsonify
import logging
from flask_jwt_extended import jwt_required
import gc
from transformers import AutoModelForCausalLM, AutoTokenizer
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint for Qwen chat routes
qwen_chat_bp = Blueprint('qwen_chat', __name__, url_prefix='/api/qwen')

# ============================================================================
# FUCKING HARDCODED PATHS
# ============================================================================
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
MODEL_PATH = PROJECT_ROOT / 'model_cache' / 'Qwen--Qwen2.5-1.5B-Instruct'

# Global variables
model = None
tokenizer = None
model_loaded = False
device = None

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
            logger.info("⚠️  Using CPU")
    return device

def load_qwen_model():
    """Load Qwen model from cache"""
    global model, tokenizer, model_loaded
    
    if model_loaded:
        return True
    
    logger.info("="*60)
    logger.info(f"🚀 LOADING QWEN 2.5-1.5B MODEL FROM: {MODEL_PATH}")
    logger.info("="*60)
    
    try:
        current_device = get_device()
        
        # Load tokenizer
        logger.info(f"📦 Loading tokenizer from {MODEL_PATH}...")
        tokenizer = AutoTokenizer.from_pretrained(
            str(MODEL_PATH),
            trust_remote_code=True
        )
        
        # Set padding token
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Load model
        logger.info(f"📦 Loading model from {MODEL_PATH}...")
        
        if current_device == "cuda":
            model = AutoModelForCausalLM.from_pretrained(
                str(MODEL_PATH),
                trust_remote_code=True,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(
                str(MODEL_PATH),
                trust_remote_code=True,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True
            )
            model = model.to(current_device)
        
        model.eval()
        
        model_loaded = True
        logger.info(f"✅ QWEN MODEL LOADED on {current_device}")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to load Qwen model: {str(e)}")
        logger.error(f"   Model path: {MODEL_PATH}")
        logger.error(f"   Path exists: {MODEL_PATH.exists()}")
        model_loaded = False
        return False

def generate_qwen_response(messages, max_tokens=512, temperature=0.7):
    """Generate response from Qwen with conversation history"""
    global model, tokenizer
    
    if not model_loaded:
        if not load_qwen_model():
            return "Model not loaded. Please try again."
    
    try:
        # Format messages for Qwen 2.5 Instruct
        formatted_text = ""
        for msg in messages:
            if msg['role'] == 'user':
                formatted_text += f"<|im_start|>user\n{msg['content']}<|im_end|>\n"
            elif msg['role'] == 'assistant':
                formatted_text += f"<|im_start|>assistant\n{msg['content']}<|im_end|>\n"
            elif msg['role'] == 'system':
                formatted_text = f"<|im_start|>system\n{msg['content']}<|im_end|>\n" + formatted_text
        
        # Add final assistant prompt
        formatted_text += "<|im_start|>assistant\n"
        
        # Tokenize
        inputs = tokenizer(
            formatted_text,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        )
        
        current_device = get_device()
        inputs = {k: v.to(current_device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=temperature,
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.1,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        # Decode
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=False)
        
        # Extract assistant response
        if '<|im_start|>assistant' in full_response:
            parts = full_response.split('<|im_start|>assistant')
            if len(parts) > 1:
                assistant_response = parts[-1]
                if '<|im_end|>' in assistant_response:
                    assistant_response = assistant_response.split('<|im_end|>')[0]
                response = assistant_response.strip()
            else:
                response = full_response
        else:
            response = full_response
        
        # Clean up
        response = response.replace('<|im_start|>', '').replace('<|im_end|>', '').strip()
        
        logger.info(f"📝 Generated {len(response)} characters")
        return response
        
    except Exception as e:
        logger.error(f"❌ Generation error: {str(e)}")
        return f"Error: {str(e)}"

def quick_chat(prompt, max_tokens=256):
    """Simple one-shot chat"""
    messages = [{'role': 'user', 'content': prompt}]
    return generate_qwen_response(messages, max_tokens=max_tokens)

# =============================================
# ROUTES
# =============================================

@qwen_chat_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        
        messages = data.get('messages', [])
        max_tokens = data.get('max_tokens', 512)
        temperature = data.get('temperature', 0.7)
        
        if not messages:
            return jsonify({'success': False, 'error': 'Messages required'}), 400
        
        # Validate messages
        for msg in messages:
            if 'role' not in msg or 'content' not in msg:
                return jsonify({'success': False, 'error': 'Invalid message format'}), 400
            if msg['role'] not in ['user', 'assistant', 'system']:
                return jsonify({'success': False, 'error': 'Invalid role'}), 400
        
        # Generate
        response = generate_qwen_response(messages, max_tokens=max_tokens, temperature=temperature)
        
        return jsonify({
            'success': True,
            'response': response,
            'model': 'Qwen2.5-1.5B-Instruct',
            'tokens_generated': len(response.split())
        })
        
    except Exception as e:
        logger.error(f"❌ Chat error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@qwen_chat_bp.route('/quick', methods=['POST'])
@jwt_required()
def quick():
    """Quick chat without history"""
    try:
        data = request.get_json()
        
        prompt = data.get('prompt', '').strip()
        max_tokens = data.get('max_tokens', 256)
        
        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt required'}), 400
        
        response = quick_chat(prompt, max_tokens=max_tokens)
        
        return jsonify({
            'success': True,
            'prompt': prompt,
            'response': response,
            'model': 'Qwen2.5-1.5B-Instruct'
        })
        
    except Exception as e:
        logger.error(f"❌ Quick chat error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@qwen_chat_bp.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'success': True,
        'model_loaded': model_loaded,
        'device': get_device(),
        'model': 'Qwen2.5-1.5B-Instruct',
        'model_path': str(MODEL_PATH),
        'status': 'ready' if model_loaded else 'loading'
    })

@qwen_chat_bp.route('/load', methods=['POST'])
@jwt_required()
def load_model():
    """Manually load model"""
    try:
        if model_loaded:
            return jsonify({
                'success': True,
                'message': 'Model already loaded',
                'device': get_device()
            })
        
        success = load_qwen_model()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Model loaded successfully',
                'device': get_device()
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to load model'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@qwen_chat_bp.route('/capabilities', methods=['GET'])
def capabilities():
    """Get model capabilities"""
    return jsonify({
        'success': True,
        'model': 'Qwen2.5-1.5B-Instruct',
        'capabilities': [
            'Text generation',
            'Conversation',
            'Code generation',
            'Question answering',
            'Creative writing',
            'Text summarization',
            'Translation',
            'Explanation'
        ],
        'max_tokens': 2048,
        'supports_system_prompt': True,
        'context_window': '8K tokens'
    })

@qwen_chat_bp.route('/system-prompt', methods=['POST'])
@jwt_required()
def system_prompt():
    """Generate response with system prompt"""
    try:
        data = request.get_json()
        
        system_prompt = data.get('system_prompt', '').strip()
        user_prompt = data.get('user_prompt', '').strip()
        max_tokens = data.get('max_tokens', 512)
        
        if not user_prompt:
            return jsonify({'success': False, 'error': 'User prompt required'}), 400
        
        # Format messages
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': user_prompt})
        
        response = generate_qwen_response(messages, max_tokens=max_tokens)
        
        return jsonify({
            'success': True,
            'system_prompt': system_prompt,
            'user_prompt': user_prompt,
            'response': response
        })
        
    except Exception as e:
        logger.error(f"❌ System prompt error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@qwen_chat_bp.route('/clear-memory', methods=['POST'])
@jwt_required()
def clear_memory():
    """Clear memory"""
    try:
        global model, tokenizer, model_loaded
        model = None
        tokenizer = None
        model_loaded = False
        
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        return jsonify({
            'success': True,
            'message': 'Memory cleared successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Pre-load model
logger.info("📄 Pre-loading Qwen model...")
try:
    load_qwen_model()
except Exception as e:
    logger.warning(f"⚠️ Could not pre-load model: {e}")