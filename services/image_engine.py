"""
Image Engine - Main Entry Point

Uses cascading fallback system:
1. Local Stable Diffusion (Hugging Face diffusers) - PRIMARY - FREE, GPU
2. Stability AI API - FALLBACK 1 - Requires API key
3. Pollinations.ai - FALLBACK 2 - FREE, no API key

See image_engine_diffusers.py for implementation
"""

from services.image_engine_diffusers import generate_image

__all__ = ["generate_image"]
