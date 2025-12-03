"""
Shared Model Configuration
Import this FIRST in all routes that use AI models
"""

import os
from pathlib import Path

# ============================================================================
# CRITICAL: Set cache directory BEFORE any transformers/torch imports
# ============================================================================

# Get the project root directory (E:\LLMs_test)
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
CACHE_DIR = str(PROJECT_ROOT / 'model_cache')  # E:\LLMs_test\model_cache

# Set ALL relevant environment variables
os.environ['HF_HOME'] = CACHE_DIR
os.environ['TRANSFORMERS_CACHE'] = CACHE_DIR
os.environ['TORCH_HOME'] = CACHE_DIR
os.environ['HF_DATASETS_CACHE'] = CACHE_DIR
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Force offline mode to use cache only
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

# Model configuration
MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

# DIRECT PATH to the downloaded model
MODEL_PATH = str(PROJECT_ROOT / 'model_cache' / 'Qwen--Qwen2.5-1.5B-Instruct')

def get_model_kwargs(device='cpu'):
    """Get model loading kwargs for specific device"""
    kwargs = {
        'trust_remote_code': True,
        'low_cpu_mem_usage': True,
    }
    
    if device == 'cuda':
        kwargs['torch_dtype'] = 'auto'
        kwargs['device_map'] = 'auto'
    else:
        kwargs['torch_dtype'] = 'float32'
        kwargs['device_map'] = None
    
    return kwargs

# Print configuration on import
print(f"🔧 Model Config Loaded:")
print(f"   📁 Cache: {CACHE_DIR}")
print(f"   📁 Model Path: {MODEL_PATH}")
print(f"   🤖 Model: {MODEL_NAME}")
print(f"   📴 Offline Mode: Enabled")