from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import logging
import time

# Import our custom AI engines
from services.text_engine import process_narrative
from services.image_engine import generate_image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with response timeout settings
app = FastAPI(
    title="The Pitch Visualizer",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount the static folder so the web page can access the saved images and CSS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 for HTML templates
templates = Jinja2Templates(directory="templates")

# Define the data structure we expect from the frontend
class StoryboardRequest(BaseModel):
    text: str
    style: str = "cinematic, photorealistic"

# Route 1: Load the main web page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serves the main HTML interface."""
    return templates.TemplateResponse("index.html", {"request": request})

# Route 2: The API endpoint that generates the storyboard
@app.post("/generate")
def generate_storyboard(req: StoryboardRequest):
    """
    1. Receives text and style from user.
    2. Uses Groq to split text into scenes and write prompts.
    3. Uses Hugging Face to generate an image for each prompt.
    4. Returns the compiled storyboard.
    """
    logger.info("=" * 60)
    logger.info("API REQUEST: /generate")
    logger.info(f"Style: {req.style}")
    logger.info(f"Text length: {len(req.text)} characters")
    logger.info(f"Text preview: {req.text[:100]}...")
    logger.info("=" * 60)

    # Step 1: Get scenes and prompts from Groq
    logger.info("Calling process_narrative() to generate scenes...")
    scenes = process_narrative(req.text, req.style)

    logger.info(f"Received {len(scenes)} scenes from process_narrative()")
    for i, s in enumerate(scenes):
        logger.info(f"  Scene {i+1}: {s.get('scene_label', 'Unknown')}")

    storyboard = []

    # Step 2: Generate an image for each scene
    for index, scene in enumerate(scenes):
        logger.info("=" * 40)
        logger.info(f"Generating image {index + 1}/{len(scenes)}...")
        logger.info(f"  Scene Label: {scene.get('scene_label', f'Scene {index + 1}')}")
        logger.info(f"  Emotional Tone: {scene.get('emotional_tone', 'neutral')}")
        logger.info(f"  Prompt: {scene['image_prompt'][:150]}...")

        # Call Pollinations.ai API with rate limiting awareness
        image_url = generate_image(scene['image_prompt'])

        if image_url:
            logger.info(f"✓ Image {index + 1} generated: {image_url}")
        else:
            logger.error(f"✗ Image {index + 1} generation FAILED")

        # Add the completed panel to our storyboard
        storyboard.append({
            "scene_number": scene.get("scene_number", index + 1),
            "scene_label": scene.get("scene_label", f"Scene {index + 1}"),
            "emotional_tone": scene.get("emotional_tone", "neutral"),
            "text": scene["scene_text"],
            "prompt": scene["image_prompt"],
            "image_url": image_url or "https://via.placeholder.com/512?text=Image+Generation+Failed"
        })
        
        # Add delay between requests to avoid rate limiting (except for last image)
        if index < len(scenes) - 1:
            logger.info("Waiting 2 seconds before next image (rate limiting prevention)...")
            time.sleep(2)

    logger.info("=" * 60)
    logger.info(f"Storyboard Complete! Generated {len(storyboard)} slides")
    logger.info("=" * 60)

    # Return the final array of data back to the web interface
    return {"status": "success", "storyboard": storyboard}

# This allows us to run the file directly
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)