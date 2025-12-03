"""
Fixed Model Download Script with better error handling and loading from custom cache
"""

import os
import sys
import time
import shutil
from pathlib import Path

# ============================================================================
# Set cache location
# ============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(SCRIPT_DIR, 'model_cache')

# Create cache directory
os.makedirs(CACHE_DIR, exist_ok=True)

print(f"\n📁 Cache location: {CACHE_DIR}")

# Check disk space
def get_free_space_gb(path):
    stat = shutil.disk_usage(path)
    return stat.free / (1024**3)

free_space = get_free_space_gb(CACHE_DIR)
print(f"💿 Available disk space: {free_space:.2f} GB")

if free_space < 8:
    print("⚠️  WARNING: Less than 8 GB free space!")
    response = input("Continue anyway? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        sys.exit(0)

print("\n" + "="*70)
print("🔄 Alternative Download Method")
print("="*70)

# Try using huggingface_hub for more reliable downloads
try:
    from huggingface_hub import snapshot_download
    import torch
    print("✅ Libraries imported successfully")
except ImportError:
    print("Installing required packages...")
    os.system("pip install huggingface_hub torch transformers accelerate")
    from huggingface_hub import snapshot_download
    import torch

# Clear cache first (optional)
cache_path = Path(CACHE_DIR)
if cache_path.exists():
    print("🧹 Cleaning old cache files...")
    # Keep only essential files
    for item in cache_path.iterdir():
        if item.name.startswith("models--Qwen"):
            shutil.rmtree(item)
            print(f"   Removed: {item.name}")

# Download model using snapshot_download (more reliable)
MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"

print(f"\n📥 Downloading: {MODEL_ID}")
print("   This may take 5-10 minutes...")

try:
    start_time = time.time()
    
    # Download with retry mechanism
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"\n   Attempt {attempt + 1}/{max_retries}")
            
            # Download the model - use a simpler approach
            local_dir = snapshot_download(
                repo_id=MODEL_ID,
                local_dir=os.path.join(CACHE_DIR, MODEL_ID.replace("/", "--")),
                local_dir_use_symlinks=False,
                resume_download=True
            )
            
            elapsed = time.time() - start_time
            print(f"\n✅ Download completed in {elapsed:.1f} seconds")
            print(f"📁 Model saved to: {local_dir}")
            
            # Verify files
            model_files = list(Path(local_dir).glob("*.safetensors")) + list(Path(local_dir).glob("*.bin"))
            config_files = list(Path(local_dir).glob("*.json"))
            
            print(f"📊 Files downloaded:")
            print(f"   - Model files: {len(model_files)}")
            print(f"   - Config files: {len(config_files)}")
            
            for file in model_files[:3]:  # Show first 3 model files
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"      {file.name} ({size_mb:.1f} MB)")
            
            break  # Success, exit retry loop
            
        except Exception as e:
            print(f"   ❌ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print("   🔄 Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("   💥 All attempts failed")
                raise
    
    # FIX: Set the actual local directory path for loading
    # The model is in your custom cache directory, not the default HF cache
    local_model_path = os.path.join(CACHE_DIR, MODEL_ID.replace("/", "--"))
    
    print(f"\n🧪 Loading model from: {local_model_path}")
    
    # First, let's see what files we have
    print("\n📁 Listing downloaded files:")
    for file in Path(local_model_path).rglob("*"):
        if file.is_file():
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"   {file.relative_to(local_model_path)} ({size_mb:.1f} MB)")
    
    # Verify the model can be loaded from local directory
    print("\n🧪 Testing model loading...")
    
    from transformers import AutoTokenizer, AutoModelForCausalLM
    
    start = time.time()
    
    try:
        # Try loading from local path directly
        tokenizer = AutoTokenizer.from_pretrained(
            local_model_path,  # Use the local path directly
            trust_remote_code=True
        )
    except Exception as e:
        print(f"   ⚠️ First attempt failed: {e}")
        print("   🔄 Trying alternative loading method...")
        
        # Alternative: Check if there's a symlink issue
        # Sometimes the files are in subdirectories
        possible_paths = [
            local_model_path,
            os.path.join(local_model_path, "snapshots", next(os.listdir(os.path.join(local_model_path, "snapshots"))) if os.path.exists(os.path.join(local_model_path, "snapshots")) else ""),
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and any(f.endswith('.json') for f in os.listdir(path)):
                print(f"   🔍 Trying path: {path}")
                try:
                    tokenizer = AutoTokenizer.from_pretrained(
                        path,
                        trust_remote_code=True
                    )
                    print(f"   ✅ Tokenizer loaded from: {path}")
                    break
                except:
                    continue
    
    print(f"   ✅ Tokenizer loaded")
    
    # Load the model from the same local path
    model = AutoModelForCausalLM.from_pretrained(
        local_model_path,  # Use the local path directly
        trust_remote_code=True,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
        device_map="auto" if torch.cuda.is_available() else "cpu"
    )
    
    load_time = time.time() - start
    print(f"   ✅ Model loaded in {load_time:.2f} seconds")
    
    # Test inference
    print("\n🧪 Testing inference...")
    test_prompt = "What is the capital of France?"
    inputs = tokenizer(test_prompt, return_tensors="pt")
    
    # Move to GPU if available
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=20,
            do_sample=True,
            temperature=0.7
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"   🤖 Model response: {response}")
    
    print("\n" + "="*70)
    print("🎉 SUCCESS! Model is ready to use")
    print("="*70)
    
    # Clean up
    del tokenizer, model
    torch.cuda.empty_cache()
    import gc
    gc.collect()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
    # Debug: Check what's in the cache directory
    print("\n🔍 Debug - Cache directory contents:")
    for root, dirs, files in os.walk(CACHE_DIR):
        level = root.replace(CACHE_DIR, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            if file.endswith(('.json', '.safetensors', '.txt', '.model')):
                print(f'{subindent}{file}')
    
    sys.exit(1)