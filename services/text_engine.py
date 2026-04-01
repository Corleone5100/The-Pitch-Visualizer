import os
import json
import logging
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def _analyze_narrative_context(text: str) -> dict:
    """
    PASS 1: Analyze the narrative to extract deep contextual understanding.
    This creates a 'story bible' that will guide all scene generation for consistency.
    Uses story arc detection to recommend optimal number of scenes (3-6).
    """
    logger.info("=" * 60)
    logger.info("PASS 1: NARRATIVE CONTEXT ANALYSIS")
    logger.info("=" * 60)
    logger.info(f"Input text length: {len(text)} characters")
    logger.info(f"Input text preview: {text[:100]}...")
    
    analysis_prompt = f"""
    You are a Story Analyst and Narrative Interpreter for a visual presentation AI.
    Your job is to DEEPLY UNDERSTAND the narrative text and extract its core elements.

    Read the following customer success story and analyze it comprehensively:

    NARRATIVE TEXT:
    "{text}"

    Extract the following elements and respond ONLY with valid JSON:

    {{
      "protagonist": {{
        "description": "Who is the main character/entity? Be specific (role, demographics if mentioned, key traits)",
        "visual_anchor": "A concise visual description to maintain character consistency across all images (e.g., 'South Asian businesswoman in 30s, navy blazer, professional demeanor')"
      }},
      "setting": {{
        "primary_location": "Where does most of the action take place?",
        "visual_elements": "Key environmental details that should appear consistently (e.g., 'modern glass-walled office, open-plan workspace')"
      }},
      "story_arc": {{
        "initial_state": "What was the situation BEFORE? (the problem/pain)",
        "catalyst": "What triggered the change? (the decision/discovery moment)",
        "transformation": "What happened DURING? (implementation/process)",
        "resolution": "What was the outcome AFTER? (results/metrics)"
      }},
      "emotional_journey": ["emotion at start", "emotion during turning point", "emotion at resolution"],
      "visual_metaphors": {{
        "problem_metaphor": "Visual metaphor for the pain point (e.g., 'drowning in paperwork', 'lost in maze')",
        "solution_metaphor": "Visual metaphor for the solution (e.g., 'light breaking through clouds', 'puzzle pieces connecting')"
      }},
      "key_themes": ["theme 1", "theme 2", "theme 3"],
      "story_complexity": {{
        "word_count": 0,
        "distinct_events": 0,
        "emotional_shifts": 0,
        "narrative_type": "simple|standard|complex",
        "detected_beats": ["beat 1", "beat 2", ...]
      }},
      "scene_recommendation": {{
        "recommended_count": 4,
        "min_count": 3,
        "max_count": 6,
        "reasoning": "Brief explanation of why this count was chosen"
      }}
    }}

    === SCENE COUNT GUIDELINES ===
    
    Analyze the narrative and recommend scene count based on these rules:
    
    **3 SCENES (Simple)**: 
    - Short text (<150 words)
    - Single problem → solution arc
    - No detailed implementation phase
    - Example: "We had a problem. We found a solution. It worked."
    
    **4 SCENES (Standard)**:
    - Medium text (150-300 words)
    - Clear problem → turning point → solution → results structure
    - Most customer success stories fit here
    - Example: "Problem was bad. Then we discovered X. We implemented it. Results were great."
    
    **5 SCENES (Complex)**:
    - Longer text (300-500 words)
    - Multiple phases or stakeholders
    - Detailed implementation process
    - Example: "Problem existed. Team searched for solutions. Evaluated options. Implemented chosen solution. Saw results."
    
    **6 SCENES (Very Complex)**:
    - Long text (500+ words)
    - Multi-phase transformation
    - Before/during/after with multiple metrics
    - Future vision or scaling mentioned
    - Example: "Old way was broken. Crisis point reached. Explored solutions. Pilot program. Full rollout. Measurable success + future plans."

    CRITICAL: Your analysis will be used to generate visually consistent storyboard images.
    Be specific, interpretive, and focus on VISUALIZABLE elements.
    The scene count must be between 3-6 (inclusive).
    """

    try:
        logger.info("Calling Groq API for context analysis...")
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a narrative analyst. Respond ONLY with valid JSON."},
                {"role": "user", "content": analysis_prompt}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.5
        )

        response_content = chat_completion.choices[0].message.content
        logger.info("Received response from Groq API")
        
        context = json.loads(response_content)
        
        # Guardrail 1: Enforce min/max bounds on scene count
        scene_rec = context.get('scene_recommendation', {})
        recommended_count = scene_rec.get('recommended_count', 4)
        
        if recommended_count < 3:
            logger.warning(f"Recommended count {recommended_count} below minimum. Setting to 3.")
            recommended_count = 3
        elif recommended_count > 6:
            logger.warning(f"Recommended count {recommended_count} above maximum. Setting to 6.")
            recommended_count = 6
        
        context['scene_recommendation']['recommended_count'] = recommended_count
        context['scene_recommendation']['min_count'] = 3
        context['scene_recommendation']['max_count'] = 6
        
        logger.info("-" * 40)
        logger.info("EXTRACTED CONTEXT:")
        logger.info(f"  • Protagonist: {context['protagonist']['description']}")
        logger.info(f"  • Visual Anchor: {context['protagonist']['visual_anchor']}")
        logger.info(f"  • Setting: {context['setting']['primary_location']}")
        logger.info(f"  • Visual Elements: {context['setting']['visual_elements']}")
        logger.info(f"  • Emotional Journey: {' → '.join(context['emotional_journey'])}")
        logger.info(f"  • Story Arc: {context['story_arc']['initial_state'][:50]}... → {context['story_arc']['resolution'][:50]}...")
        logger.info(f"  • Problem Metaphor: {context['visual_metaphors']['problem_metaphor']}")
        logger.info(f"  • Solution Metaphor: {context['visual_metaphors']['solution_metaphor']}")
        
        complexity = context.get('story_complexity', {})
        logger.info("-" * 40)
        logger.info("STORY COMPLEXITY ANALYSIS:")
        logger.info(f"  • Word Count: {complexity.get('word_count', 'N/A')}")
        logger.info(f"  • Distinct Events: {complexity.get('distinct_events', 'N/A')}")
        logger.info(f"  • Emotional Shifts: {complexity.get('emotional_shifts', 'N/A')}")
        logger.info(f"  • Narrative Type: {complexity.get('narrative_type', 'standard').upper()}")
        logger.info(f"  • Detected Story Beats: {', '.join(complexity.get('detected_beats', ['N/A']))}")
        
        logger.info("-" * 40)
        logger.info("SCENE RECOMMENDATION:")
        logger.info(f"  • Recommended Count: {recommended_count} scenes")
        logger.info(f"  • Valid Range: 3-6 scenes")
        logger.info(f"  • Reasoning: {scene_rec.get('reasoning', 'Based on story complexity analysis')}")
        logger.info("-" * 40)
        
        return context

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error in context analysis: {e}")
        logger.error(f"Raw response: {response_content[:200] if 'response_content' in locals() else 'N/A'}")
        return get_fallback_context()
    except Exception as e:
        logger.error(f"Error in context analysis: {e}")
        return get_fallback_context()


def get_fallback_context() -> dict:
    """Returns a fallback context when analysis fails."""
    logger.warning("Using fallback context due to analysis failure")
    return {
        "protagonist": {"description": "business professional", "visual_anchor": "professional business person in corporate attire"},
        "setting": {"primary_location": "office environment", "visual_elements": "modern corporate office"},
        "story_arc": {"initial_state": "facing challenges", "catalyst": "discovered solution", "transformation": "implemented change", "resolution": "achieved success"},
        "emotional_journey": ["stressed", "hopeful", "triumphant"],
        "visual_metaphors": {"problem_metaphor": "overwhelmed by workload", "solution_metaphor": "streamlined efficiency"},
        "key_themes": ["transformation", "success", "innovation"],
        "story_complexity": {"narrative_type": "standard"},
        "scene_recommendation": {"recommended_count": 4, "min_count": 3, "max_count": 6, "reasoning": "Fallback to standard 4-scene structure"}
    }


def get_scene_description(scene_num: int, total_scenes: int) -> str:
    """Get description for a scene based on its position and total count."""
    descriptions = {
        (1, 3): "Establish the protagonist and their initial challenge",
        (2, 3): "Show the solution being introduced or discovered",
        (3, 3): "Show the transformed outcome with results",
        (1, 4): "Show the protagonist struggling with the initial challenge",
        (2, 4): "Show the moment of realization or discovery of the solution",
        (3, 4): "Show the protagonist actively using/implementing the solution",
        (4, 4): "Show the transformed outcome with measurable results",
        (1, 5): "Establish the problem and its impact",
        (2, 5): "Show the search for solutions",
        (3, 5): "Show the decision moment",
        (4, 5): "Show the implementation process",
        (5, 5): "Show the results and transformation",
        (1, 6): "Show the old way and its problems",
        (2, 6): "Show the crisis point",
        (3, 6): "Show the discovery of potential solutions",
        (4, 6): "Show the pilot program or testing",
        (5, 6): "Show the full rollout",
        (6, 6): "Show the future vision and success"
    }
    return descriptions.get((scene_num, total_scenes), "Show the story progressing")


def get_mood_for_scene(scene_num: int, total_scenes: int) -> str:
    """Get visual mood for a scene based on its position in the arc."""
    progress = scene_num / total_scenes
    
    if progress <= 0.25:
        return "Tense, dark, or chaotic - emphasize the problem"
    elif progress <= 0.5:
        return "Transition - hint of hope, light beginning to break through"
    elif progress <= 0.75:
        return "Active, engaged, focused - show the work happening"
    else:
        return "Bright, open, triumphant - show the success"


def _generate_scenes_with_context(text: str, context: dict, style: str) -> list:
    """
    PASS 2: Generate scenes using the extracted context for deep interpretation and consistency.
    Uses dynamic scene count (3-6) based on story complexity analysis.
    """
    logger.info("=" * 60)
    logger.info("PASS 2: SCENE GENERATION")
    logger.info("=" * 60)
    
    # Get dynamic scene count from context analysis
    scene_rec = context.get('scene_recommendation', {})
    num_scenes = scene_rec.get('recommended_count', 4)
    min_scenes = scene_rec.get('min_count', 3)
    max_scenes = scene_rec.get('max_count', 6)
    
    logger.info(f"Dynamic scene count: {num_scenes} scenes (range: {min_scenes}-{max_scenes})")
    logger.info(f"Reasoning: {scene_rec.get('reasoning', 'Based on story complexity')}")
    
    # Build the visual consistency token
    visual_consistency_token = (
        f"VISUAL CONSISTENCY REQUIREMENTS: "
        f"Protagonist: {context['protagonist']['visual_anchor']}. "
        f"Setting: {context['setting']['visual_elements']}. "
        f"Maintain these elements across ALL {num_scenes} scenes for visual continuity."
    )
    
    logger.info(f"Visual consistency token: {visual_consistency_token[:100]}...")
    
    # Dynamic scene labels based on count
    scene_labels_map = {
        3: ["The Problem", "The Solution", "The Results"],
        4: ["The Problem", "The Turning Point", "The Transformation", "The Resolution"],
        5: ["The Problem", "The Search", "The Decision", "The Implementation", "The Results"],
        6: ["The Old Way", "The Crisis", "The Discovery", "The Pilot", "The Rollout", "The Future"]
    }
    scene_labels = scene_labels_map.get(num_scenes, scene_labels_map[4])
    emotional_journey = context.get('emotional_journey', ['stressed', 'hopeful', 'focused', 'engaged', 'triumphant'])

    # Build scene descriptions dynamically
    scene_descriptions = ""
    for i in range(1, num_scenes + 1):
        metaphor = context['visual_metaphors']['problem_metaphor'] if i <= num_scenes//2 else context['visual_metaphors']['solution_metaphor']
        scene_descriptions += f"""
    SCENE {i} - {scene_labels[i-1]}:
    - {get_scene_description(i, num_scenes)}
    - Visual mood: {get_mood_for_scene(i, num_scenes)}
    - Use visual metaphor: {metaphor}
"""

    # Build output format dynamically - simpler structure
    scenes_array_template = []
    for i in range(1, num_scenes + 1):
        emotion_idx = min(i - 1, len(emotional_journey) - 1)
        emotion = emotional_journey[emotion_idx] if emotion_idx < len(emotional_journey) else 'neutral'
        scenes_array_template.append({
            "scene_number": i,
            "scene_label": scene_labels[i-1],
            "scene_text": "Exact quote from narrative (15-25 words)",
            "image_prompt": "Full detailed prompt following the formula",
            "emotional_tone": emotion,
            "visual_focus": "What the viewer's eye should focus on"
        })

    scene_generation_prompt = f"""
    You are an expert Storyboard Artist and Visual Narrative Designer.

    Your task: Transform the narrative into a {num_scenes}-scene visual storyboard that tells a COHERENT,
    SEQUENTIAL story with clear progression from problem to resolution.

    === STORY CONTEXT (from analysis) ===
    Protagonist: {context['protagonist']['description']}
    Setting: {context['setting']['primary_location']}

    Story Arc:
    - Initial State: {context['story_arc']['initial_state'][:100]}
    - Catalyst: {context['story_arc']['catalyst'][:100]}
    - Transformation: {context['story_arc']['transformation'][:100]}
    - Resolution: {context['story_arc']['resolution'][:100]}

    Emotional Journey: {', '.join(emotional_journey)}

    Visual Metaphors:
    - Problem: {context['visual_metaphors']['problem_metaphor'][:100]}
    - Solution: {context['visual_metaphors']['solution_metaphor'][:100]}

    Story Complexity:
    - Narrative Type: {context.get('story_complexity', {}).get('narrative_type', 'standard')}
    - Recommended Scenes: {num_scenes} (based on complexity analysis)

    {visual_consistency_token}

    === WHY {num_scenes} SCENES? ===
    {scene_rec.get('reasoning', f'This narrative requires {num_scenes} scenes to tell the complete story.')}

    === YOUR TASK ===
{scene_descriptions}
    === IMAGE PROMPT FORMULA (MANDATORY) ===

    Every image prompt MUST follow this exact structure:

    "[SPECIFIC SUBJECT with consistent protagonist details] + [ACTION/STATE] + in [DETAILED ENVIRONMENT] + with [LIGHTING/MOOD] + and [COMPOSITION], {style}"

    === CRITICAL GUIDELINES ===

    1. DEEP INTERPRETATION: Interpret the MEANING, not just the words.
    2. SEQUENTIAL PROGRESSION: Each scene must show CLEAR CHANGE from the previous.
    3. VISUAL CONSISTENCY: Same protagonist and setting across all {num_scenes} scenes.
    4. SCENE TEXT: Extract 15-25 word snippets from the narrative for each scene.

    === NARRATIVE TEXT TO PROCESS ===
    {text}

    === OUTPUT FORMAT ===

    Respond ONLY with valid JSON. No markdown, no code blocks, no explanations.

    {{"scenes": [
        {{"scene_number": 1, "scene_label": "{scene_labels[0]}", "scene_text": "...", "image_prompt": "...", "emotional_tone": "{scenes_array_template[0]['emotional_tone']}", "visual_focus": "..."}},
        {{"scene_number": 2, "scene_label": "{scene_labels[1]}", "scene_text": "...", "image_prompt": "...", "emotional_tone": "{scenes_array_template[1]['emotional_tone']}", "visual_focus": "..."}}{', ' + ', '.join([f'{{"scene_number": {i+1}, "scene_label": "{scene_labels[i]}", "scene_text": "...", "image_prompt": "...", "emotional_tone": "{scenes_array_template[i]["emotional_tone"]}", "visual_focus": "..."}}' for i in range(2, num_scenes)]) if num_scenes > 2 else ''}
    ]}}

    IMPORTANT: Return exactly {num_scenes} scenes.
"""

    try:
        logger.info("Calling Groq API for scene generation...")
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a storyboard artist. Respond ONLY with valid JSON."},
                {"role": "user", "content": scene_generation_prompt}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.8
        )

        response_content = chat_completion.choices[0].message.content
        logger.info("Received response from Groq API")
        logger.info(f"Response length: {len(response_content)} characters")
        
        # Log full response for debugging
        logger.debug(f"Raw LLM response:\n{response_content}")
        logger.info(f"Raw response preview: {response_content[:800]}...")
        
        # Try to parse JSON
        try:
            parsed_json = json.loads(response_content)
            logger.info("JSON parsing successful")
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON parsing failed: {json_err}")
            logger.error(f"Problematic response:\n{response_content}")
            # Try to extract scenes array with regex as fallback
            import re
            scenes_match = re.search(r'"scenes"\s*:\s*\[(.*?)\]', response_content, re.DOTALL)
            if scenes_match:
                logger.warning("Attempting to salvage partial JSON...")
                # This is a best-effort fallback
                return []
            return []
        
        scenes = parsed_json.get("scenes", [])
        
        logger.info(f"Parsed {len(scenes)} scenes from JSON response")
        
        # Guardrail 2: Validate scene count matches expectation
        if len(scenes) != num_scenes:
            logger.warning(f"Expected {num_scenes} scenes but got {len(scenes)}. Adjusting...")
            if len(scenes) > max_scenes:
                scenes = scenes[:max_scenes]
                logger.info(f"Truncated to {max_scenes} scenes (maximum allowed)")
            elif len(scenes) < min_scenes:
                logger.warning(f"Only {len(scenes)} scenes generated (below minimum {min_scenes})")
        
        if len(scenes) > 0:
            logger.info("-" * 40)
            logger.info(f"GENERATED SCENES ({len(scenes)} total):")
            for i, scene in enumerate(scenes):
                logger.info(f"\n  SCENE {i+1}: {scene.get('scene_label', 'Unknown')}")
                logger.info(f"    • Scene Text: {scene.get('scene_text', 'N/A')[:80]}...")
                logger.info(f"    • Emotional Tone: {scene.get('emotional_tone', 'N/A')}")
                logger.info(f"    • Image Prompt: {scene.get('image_prompt', 'N/A')[:150]}...")
            logger.info("-" * 40)
        else:
            logger.warning("No scenes were generated from the LLM response")
        
        return scenes

    except Exception as e:
        logger.error(f"Error in scene generation: {e}", exc_info=True)
        logger.error(f"Error type: {type(e).__name__}")
        return []


def process_narrative(text: str, style: str = "cinematic, photorealistic") -> list:
    """
    Main entry point: Two-pass narrative processing for intelligent storyboard generation.

    PASS 1: Deep Context Analysis
    - Extract protagonist, setting, story arc, emotional journey
    - Identify visual metaphors and key themes
    - Analyze story complexity to recommend optimal scene count (3-6)
    - Create a 'story bible' for visual consistency

    PASS 2: Scene Generation with Context
    - Generate dynamic number of scenes (3-6) based on complexity
    - Apply visual consistency tokens to every prompt
    - Use deep interpretation guidelines for meaningful prompts

    This approach ensures:
    - Visual continuity across all storyboard panels
    - Semantic understanding, not just text splitting
    - Emotional progression that matches the narrative arc
    - Rich, interpretive image prompts that capture meaning, not just words
    - Dynamic scene count that adapts to story complexity
    """
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 10 + "THE PITCH VISUALIZER - PROCESS NARRATIVE" + " " * 9 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    
    # PASS 1
    context = _analyze_narrative_context(text)
    
    # PASS 2
    scenes = _generate_scenes_with_context(text, context, style)
    
    if not scenes:
        logger.error("Scene generation failed, using fallback...")
        return [{
            "scene_number": 1,
            "scene_label": "Fallback Scene",
            "scene_text": text[:100] + "..." if len(text) > 100 else text,
            "image_prompt": f"A professional business scene showing: {text[:50]}..., {style}",
            "emotional_tone": "neutral",
            "visual_focus": "main subject"
        }]
    
    logger.info("=" * 60)
    logger.info(f"FINAL OUTPUT: {len(scenes)} scenes ready for image generation")
    logger.info("=" * 60)
    
    return scenes
