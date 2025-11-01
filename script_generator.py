"""
Script Generator - Create narration scripts from timeline data
Generates JSON scripts for HeyGen avatar narration
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class ScriptSegment(BaseModel):
    """A segment of the narration script"""
    segment_id: int = Field(description="Sequential segment number (0=intro, 1+=content)")
    segment_type: str = Field(description="Type: 'intro' or 'narration'")
    start_time: float = Field(description="Start time in seconds (0 for intro)")
    duration: float = Field(description="Duration in seconds")
    narration_text: str = Field(description="What the avatar says in this segment")
    context: str = Field(description="What's happening in the browser at this time")


class VideoScript(BaseModel):
    """Complete video narration script"""
    course_title: str = Field(description="Title of the course")
    product_name: str = Field(description="Name of the product")
    total_duration: float = Field(description="Total video duration in seconds")
    intro_duration: float = Field(description="Duration of intro in seconds")
    segments: List[ScriptSegment] = Field(description="Ordered list of script segments")


class ScriptGenerator:
    """Generate narration scripts from timeline data"""
    
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
    
    def generate_script(
        self,
        timeline_data: Dict[str, Any],
        course_data: Dict[str, Any],
        product_context: Dict[str, Any]
    ) -> VideoScript:
        """Generate video script from timeline and course data."""
        
        print(f"\n📝 Generating video script for: {timeline_data.get('course_title', 'Course')}")
        
        # Build prompt
        prompt = self._build_script_prompt(timeline_data, course_data, product_context)
        
        try:
            # Use o3-mini with structured outputs
            response = self.client.chat.completions.parse(
                model="o3-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional video script writer who creates engaging, concise narration for tutorial videos. You write clear, friendly scripts that guide viewers through software demonstrations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format=VideoScript,
                max_completion_tokens=8000
            )
            
            script = response.choices[0].message.parsed
            
            print(f"   ✅ Generated script with {len(script.segments)} segments")
            print(f"   📊 Total duration: {script.total_duration:.1f}s")
            print(f"   💬 Intro duration: {script.intro_duration:.1f}s")
            
            return script
            
        except Exception as e:
            print(f"   ❌ Script generation failed: {e}")
            raise
    
    def _build_script_prompt(
        self,
        timeline_data: Dict[str, Any],
        course_data: Dict[str, Any],
        product_context: Dict[str, Any]
    ) -> str:
        """Build prompt for script generation."""
        
        course_title = timeline_data.get('course_title', 'Course')
        product_name = product_context.get('product_name', 'the product')
        events = timeline_data.get('events', [])
        total_duration = timeline_data.get('duration_seconds', 0)
        
        # Extract key timeline moments
        timeline_summary = []
        for event in events:
            timeline_summary.append({
                'time': event.get('t_formatted'),
                'time_seconds': event.get('t_offset_s'),
                'url': event.get('url', ''),
                'memory': event.get('memory', '')[:200],  # Truncate for brevity
                'actions': len(event.get('actions', []))
            })
        
        prompt = f"""Create a narration script for a tutorial video about {product_name}.

COURSE INFORMATION:
Title: {course_title}
Product: {product_name}
Total Duration: {total_duration:.0f} seconds
Key Idea: {course_data.get('key_idea', 'Learn to use the product')}

TIMELINE EVENTS:
{json.dumps(timeline_summary, indent=2)[:4000]}

REQUIREMENTS:

1. INTRO SEGMENT (0):
   - segment_type: "intro"
   - start_time: 0
   - duration: 10-15 seconds
   - Create a welcoming introduction that:
     * Greets the viewer
     * States what this tutorial will teach
     * Mentions the product name
     * Sets expectations (brief and encouraging)
   - Keep it concise and friendly!

2. NARRATION SEGMENTS (1+):
   - segment_type: "narration"
   - Create 5-8 segments covering the main parts of the tutorial
   - Each segment should:
     * start_time: Match timeline events (use t_offset_s from events)
     * duration: 5-15 seconds (brief narration)
     * narration_text: What to say (as if you're demonstrating)
     * context: What's happening in the browser
   - Narration should be:
     * Concise (1-2 sentences per segment)
     * Action-oriented ("Now I'm clicking...", "Here we're entering...")
     * Natural and conversational
     * First-person ("I'm", "we're", "let's")
   
3. TIMING:
   - Intro at time 0
   - Narration segments aligned with key timeline moments
   - Don't narrate EVERY step - pick 5-8 key moments
   - Each narration: 5-15 seconds max
   
4. STYLE:
   - Friendly, professional tone
   - Speak as the demonstrator
   - Keep it simple and clear
   - Avoid jargon

Generate a complete video script with intro + narration segments.
"""
        
        return prompt
    
    def save_script(
        self,
        script: VideoScript,
        course_index: int,
        session_id: str,
        output_dir: Path
    ) -> str:
        """Save script to JSON file."""
        
        filename = output_dir / f"course_{course_index + 1}_{session_id}_script.json"
        
        with open(filename, 'w') as f:
            json.dump(script.model_dump(), f, indent=2)
        
        print(f"   💾 Script saved: {filename.name}")
        
        return str(filename)


async def main():
    """Test script generator"""
    import sys
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ OPENAI_API_KEY not found")
        return
    
    # Load latest timeline
    outputs_dir = Path('outputs')
    timeline_files = sorted(outputs_dir.glob('course_0_*_timeline.json'))
    
    if not timeline_files:
        print("❌ No timeline files found")
        return
    
    latest_timeline = timeline_files[-1]
    print(f"📂 Loading: {latest_timeline.name}\n")
    
    with open(latest_timeline) as f:
        timeline_data = json.load(f)
    
    # Load course data
    demo_files = sorted(outputs_dir.glob('demos_*.json'))
    if demo_files:
        with open(demo_files[-1]) as f:
            demos_data = json.load(f)
            course_data = demos_data['demos'][0]  # First course
    else:
        course_data = {'key_idea': 'Learn to use the product'}
    
    # Product context
    product_context = {
        'product_name': 'SpinStack',
        'product_overview': 'AI workflow automation platform'
    }
    
    # Generate script
    generator = ScriptGenerator(openai_api_key=openai_key)
    script = generator.generate_script(timeline_data, course_data, product_context)
    
    # Save script
    session_id = timeline_data.get('session_id', 'test')
    script_file = generator.save_script(script, 0, session_id, outputs_dir)
    
    print(f"\n✅ Script generated successfully!")
    print(f"   File: {script_file}")
    print(f"\n   Intro: {script.segments[0].narration_text[:100]}...")
    print(f"   Segments: {len(script.segments)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

