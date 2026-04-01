"""
Image Engine - Assessment-Compliant Implementation with Cascading Fallback

Priority Order (4-tier fallback system):
1. Local Stable Diffusion (Hugging Face diffusers) - PRIMARY - FREE, GPU
2. Stability AI API - FALLBACK 1 - High quality, requires API key
3. Hugging Face Inference API - FALLBACK 2 - Worked well before, requires API key
4. Pollinations.ai - FALLBACK 3 - FREE, no API key, last resort

This ensures maximum reliability while keeping costs zero for the primary method.
"""

import os
import uuid
import random
import time
import logging
import torch
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# ============================================
# IMAGE METHOD SELECTION (from .env)
# ============================================
# Options: local, huggingface, pollinate, auto
IMAGE_METHOD_ENV = os.getenv("IMAGE_METHOD", "auto").lower()
logger.info("="*60)
logger.info(f"IMAGE METHOD SELECTED: {IMAGE_METHOD_ENV.upper()}")
logger.info("="*60)

if IMAGE_METHOD_ENV == "auto":
    logger.info("🔄 Cascading Fallback: Local → Stability → HF API → Pollinations")
elif IMAGE_METHOD_ENV == "local":
    logger.info("💻 Using LOCAL GPU (NVIDIA RTX 3050)")
elif IMAGE_METHOD_ENV == "huggingface":
    logger.info("🌐 Using Hugging Face Inference API")
elif IMAGE_METHOD_ENV == "pollinate":
    logger.info("☁️ Using Pollinations.ai (Cloud)")
else:
    logger.info(f"⚠️ Unknown method: {IMAGE_METHOD_ENV}")

logger.info("Options: local, huggingface, pollinate, auto")
logger.info("="*60)

# ============================================
# PRIMARY: Local Stable Diffusion (Diffusers)
# ============================================
try:
    from diffusers import StableDiffusionPipeline
    DIFFUSERS_AVAILABLE = True
    logger.info("✅ Hugging Face diffusers library: AVAILABLE")
except ImportError as e:
    DIFFUSERS_AVAILABLE = False
    logger.warning(f"⚠️ diffusers library not installed: {e}")

# ============================================
# FALLBACK 1: Stability AI API
# ============================================
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_API_URL = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

if STABILITY_API_KEY:
    logger.info("✅ Stability AI API key: CONFIGURED")
else:
    logger.info("ℹ️  Stability AI API key: NOT CONFIGURED")

# ============================================
# FALLBACK 2: Hugging Face Inference API
# ============================================
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
HF_HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}

if HF_API_KEY:
    logger.info("✅ Hugging Face Inference API: CONFIGURED")
else:
    logger.info("ℹ️  Hugging Face Inference API: NOT CONFIGURED")

# ============================================
# FALLBACK 3: Pollinations.ai (Last resort)
# ============================================
POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt/"
logger.info("✅ Pollinations.ai: AVAILABLE (no API key needed)")

# ============================================
# Configuration - Optimized for 4GB GPU
# ============================================
MODEL_ID = "runwayml/stable-diffusion-v1-5"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

logger.info("="*60)
logger.info("IMAGE GENERATION SYSTEM - DEVICE CHECK")
logger.info("="*60)
logger.info(f"PyTorch Version: {torch.__version__}")
logger.info(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    logger.info(f"CUDA Version: {torch.version.cuda}")
    logger.info(f"GPU Count: {torch.cuda.device_count()}")
    logger.info(f"GPU Name: {torch.cuda.get_device_name(0)}")
    logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    logger.info(f"GPU Memory Available: {torch.cuda.mem_get_info()[1] / 1024**3:.1f} GB")
else:
    logger.info("⚠️ CUDA NOT AVAILABLE - Will use CPU (slower)")

logger.info("="*60)

# Memory optimization for 4GB GPUs
USE_HALF_PRECISION = True
ENABLE_ATTENTION_SLICING = True
ENABLE_VAE_TILING = True

# Global pipeline (loaded once)
pipeline = None


def load_pipeline():
    """Load Stable Diffusion pipeline with GPU optimization"""
    global pipeline

    if pipeline is not None:
        logger.info("✅ Using cached pipeline")
        return pipeline

    logger.info("="*60)
    logger.info("LOADING STABLE DIFFUSION MODEL")
    logger.info("="*60)
    logger.info(f"Model: {MODEL_ID}")
    logger.info(f"Device: {DEVICE}")

    if DEVICE == "cuda":
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

    logger.info("This takes 2-5 minutes on first run (model download ~7GB)")
    logger.info("Subsequent runs: ~10-20 seconds (cached)")

    try:
        # Determine dtype
        if DEVICE == "cuda" and USE_HALF_PRECISION:
            dtype = torch.float16
            logger.info("Using float16 precision (saves VRAM)")
        else:
            dtype = torch.float32
            logger.info("Using float32 precision")

        # Load pipeline
        logger.info("Loading pipeline...")
        pipeline = StableDiffusionPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=dtype,
            use_safetensors=True,
            safety_checker=None,
            requires_safety_checker=False
        )

        # Move to GPU
        if DEVICE == "cuda":
            logger.info("Moving pipeline to GPU...")
            pipeline = pipeline.to("cuda")

            # Memory optimizations
            try:
                pipeline.enable_attention_slicing(1)
                logger.info("✅ Enabled attention slicing")
            except Exception as e:
                logger.warning(f"Could not enable attention slicing: {e}")

            try:
                pipeline.enable_vae_tiling()
                logger.info("✅ Enabled VAE tiling")
            except Exception as e:
                logger.warning(f"Could not enable VAE tiling: {e}")

        logger.info("="*60)
        logger.info("✅ MODEL LOADED SUCCESSFULLY")
        logger.info("="*60)
        return pipeline

    except Exception as e:
        logger.error("="*60)
        logger.error(f"❌ FAILED TO LOAD MODEL")
        logger.error("="*60)
        logger.error(f"Error: {e}")
        logger.debug(f"Traceback:\n{traceback.format_exc()}")
        return None


def generate_image_local(prompt: str) -> str:
    """METHOD 1: Generate image using LOCAL Stable Diffusion (GPU-accelerated)"""
    logger.info("-"*60)
    logger.info("METHOD 1: LOCAL STABLE DIFFUSION (GPU) - PRIMARY")
    logger.info("-"*60)
    logger.info(f"Prompt: {prompt[:100]}...")

    if not DIFFUSERS_AVAILABLE:
        logger.warning("⚠️ diffusers not installed")
        return None

    pipe = load_pipeline()
    if pipe is None:
        logger.warning("⚠️ Pipeline failed to load")
        return None

    try:
        logger.info("Generating image on GPU...")

        image = pipe(
            prompt,
            negative_prompt="ugly, blurry, bad anatomy, text, watermarks, low quality",
            num_inference_steps=20,
            guidance_scale=7.5,
            width=512,
            height=512,
        ).images[0]

        filename = f"{uuid.uuid4().hex}.png"
        os.makedirs(os.path.join("static", "images"), exist_ok=True)
        filepath = os.path.join("static", "images", filename)
        image.save(filepath)

        logger.info(f"✅ SUCCESS: {filename}")
        return f"/static/images/{filename}"

    except torch.cuda.OutOfMemoryError as e:
        logger.error(f"❌ CUDA OUT OF MEMORY: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ LOCAL GENERATION FAILED: {e}")
        logger.debug(f"Traceback:\n{traceback.format_exc()}")
        return None


def generate_image_stability(prompt: str) -> str:
    """METHOD 2: Stability AI API (FALLBACK 1)"""
    logger.info("-"*60)
    logger.info("METHOD 2: STABILITY AI API (FALLBACK 1)")
    logger.info("-"*60)

    if not STABILITY_API_KEY:
        logger.warning("⚠️ No Stability API key configured")
        return None

    logger.info(f"Prompt: {prompt[:100]}...")

    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "image/*"
    }

    payload = {
        "prompt": prompt,
        "mode": "text-to-image",
        "seed": random.randint(0, 2**32 - 1),
        "output_format": "png",
    }

    try:
        import requests
        logger.info("Sending request to Stability AI...")
        response = requests.post(
            STABILITY_API_URL,
            headers=headers,
            files={"none": ""},
            data=payload,
            timeout=60
        )

        if response.status_code == 200:
            filename = f"{uuid.uuid4().hex}.png"
            os.makedirs(os.path.join("static", "images"), exist_ok=True)
            filepath = os.path.join("static", "images", filename)

            with open(filepath, "wb") as f:
                f.write(response.content)

            logger.info(f"✅ SUCCESS: {filename}")
            return f"/static/images/{filename}"
        else:
            logger.error(f"❌ Stability AI Error ({response.status_code}): {response.text[:200]}")
            return None

    except Exception as e:
        logger.error(f"❌ Stability AI FAILED: {e}")
        return None


def generate_image_huggingface(prompt: str) -> str:
    """METHOD 3: Hugging Face Inference API (FALLBACK 2)"""
    logger.info("-"*60)
    logger.info("METHOD 3: HUGGING FACE INFERENCE API (FALLBACK 2)")
    logger.info("-"*60)

    if not HF_API_KEY:
        logger.warning("⚠️ No Hugging Face API key configured")
        return None

    logger.info(f"Prompt: {prompt[:100]}...")

    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": "ugly, blurry, bad anatomy, text, watermarks",
            "num_inference_steps": 25
        }
    }

    try:
        import requests
        logger.info("Sending request to Hugging Face Inference API...")
        response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload, timeout=120)

        # Success
        if response.status_code == 200:
            filename = f"{uuid.uuid4().hex}.png"
            os.makedirs(os.path.join("static", "images"), exist_ok=True)
            filepath = os.path.join("static", "images", filename)

            with open(filepath, "wb") as f:
                f.write(response.content)

            logger.info(f"✅ SUCCESS: {filename}")
            return f"/static/images/{filename}"

        # Model loading (503)
        elif response.status_code == 503:
            try:
                error_data = response.json()
                wait_time = error_data.get("estimated_time", 20)
                logger.warning(f"⚠️ Model loading. Waiting {wait_time:.0f}s...")
                time.sleep(wait_time)
                # Retry once
                logger.info("Retrying...")
                response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload, timeout=120)
                if response.status_code == 200:
                    filename = f"{uuid.uuid4().hex}.png"
                    os.makedirs(os.path.join("static", "images"), exist_ok=True)
                    filepath = os.path.join("static", "images", filename)
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    logger.info(f"✅ SUCCESS (after retry): {filename}")
                    return f"/static/images/{filename}"
            except:
                pass
            logger.error("❌ Hugging Face API: Model still loading after wait")
            return None

        # Other errors
        else:
            logger.error(f"❌ Hugging Face API Error ({response.status_code}): {response.text[:200]}")
            return None

    except Exception as e:
        logger.error(f"❌ Hugging Face API FAILED: {e}")
        return None


def generate_image_pollinations(prompt: str) -> str:
    """METHOD 4: Pollinations.ai (FALLBACK 3 - LAST RESORT)"""
    logger.info("-"*60)
    logger.info("METHOD 4: POLLINATIONS.AI (FALLBACK 3 - LAST RESORT)")
    logger.info("-"*60)
    logger.info(f"Prompt: {prompt[:100]}...")

    clean_prompt = prompt.replace(" ", "%20").replace("?", "").replace('"', '').replace("'", "")
    full_url = f"{POLLINATIONS_BASE_URL}{clean_prompt}?width=1024&height=576&seed={uuid.uuid4().int}&model=flux&nologo=true"

    try:
        import requests
        logger.info("Sending request to Pollinations.ai...")
        response = requests.get(full_url, timeout=60)

        if response.status_code == 200 and len(response.content) > 0:
            filename = f"{uuid.uuid4().hex}.png"
            os.makedirs(os.path.join("static", "images"), exist_ok=True)
            filepath = os.path.join("static", "images", filename)

            with open(filepath, "wb") as f:
                f.write(response.content)

            logger.info(f"✅ SUCCESS: {filename}")
            return f"/static/images/{filename}"
        else:
            logger.error(f"❌ Pollinations Error ({response.status_code})")
            return None

    except Exception as e:
        logger.error(f"❌ Pollinations FAILED: {e}")
        return None


def generate_image(prompt: str) -> str:
    """
    Main entry point with IMAGE_METHOD selection from .env
    
    IMAGE_METHOD options:
    - local: Use ONLY Local Stable Diffusion (GPU)
    - huggingface: Use ONLY Hugging Face Inference API
    - pollinate: Use ONLY Pollinations.ai
    - auto: Use cascading fallback (RECOMMENDED)
    """
    logger.info("="*60)
    logger.info("IMAGE GENERATION - METHOD SELECTION")
    logger.info("="*60)
    
    # If IMAGE_METHOD is set to a specific method, use ONLY that method
    if IMAGE_METHOD_ENV == "local":
        logger.info("Mode: LOCAL DIFFUSERS ONLY")
        logger.info("="*60)
        if DIFFUSERS_AVAILABLE:
            result = generate_image_local(prompt)
            if result:
                return result
            logger.error("❌ Local Diffusers FAILED")
            return None
        else:
            logger.error("❌ diffusers not installed!")
            return None
    
    elif IMAGE_METHOD_ENV == "huggingface":
        logger.info("Mode: HUGGING FACE API ONLY")
        logger.info("="*60)
        logger.info("🚀 Using Hugging Face Inference API (NOT local diffusers)")
        logger.info("📡 API URL: https://router.huggingface.co/hf-inference/models/...")
        logger.info("="*60)
        if HF_API_KEY:
            result = generate_image_huggingface(prompt)
            if result:
                logger.info("✅ SUCCESS - Image generated via Hugging Face API")
                return result
            logger.error("❌ Hugging Face API FAILED")
            return None
        else:
            logger.error("❌ No HF API key configured in .env!")
            logger.error("Add this line to .env: HUGGINGFACE_API_KEY=hf_your_key")
            return None
    
    elif IMAGE_METHOD_ENV == "pollinate":
        logger.info("Mode: POLLINATIONS.AI ONLY")
        logger.info("="*60)
        result = generate_image_pollinations(prompt)
        return result
    
    elif IMAGE_METHOD_ENV == "auto":
        # CASCADING FALLBACK (default)
        logger.info("Mode: AUTO (Cascading Fallback)")
        logger.info("="*60)
        
        # METHOD 1: Local Stable Diffusion (PRIMARY)
        if DIFFUSERS_AVAILABLE:
            logger.info("Attempting Method 1: Local Stable Diffusion (GPU)...")
            result = generate_image_local(prompt)
            if result:
                logger.info("✅ Method 1 SUCCESS - Using LOCAL GPU")
                return result
            logger.warning("⚠️ Method 1 FAILED, trying fallback...")
        
        # METHOD 2: Stability AI API (FALLBACK 1)
        if STABILITY_API_KEY:
            logger.info("Attempting Method 2: Stability AI API...")
            result = generate_image_stability(prompt)
            if result:
                logger.info("✅ Method 2 SUCCESS - Using STABILITY AI")
                return result
            logger.warning("⚠️ Method 2 FAILED, trying next fallback...")
        
        # METHOD 3: Hugging Face Inference API (FALLBACK 2)
        if HF_API_KEY:
            logger.info("Attempting Method 3: Hugging Face Inference API...")
            result = generate_image_huggingface(prompt)
            if result:
                logger.info("✅ Method 3 SUCCESS - Using HUGGING FACE API")
                return result
            logger.warning("⚠️ Method 3 FAILED, trying last resort...")
        
        # METHOD 4: Pollinations.ai (LAST RESORT)
        logger.info("Attempting Method 4: Pollinations.ai (LAST RESORT)...")
        result = generate_image_pollinations(prompt)
        if result:
            logger.info("✅ Method 4 SUCCESS - Using POLLINATIONS.AI")
            return result
        
        logger.error("="*60)
        logger.error("❌ ALL METHODS FAILED")
        logger.error("="*60)
        return None
    
    else:
        logger.error(f"❌ Unknown IMAGE_METHOD: {IMAGE_METHOD_ENV}")
        logger.info("Valid options: local, huggingface, pollinate, auto")
        return None
