"""
MDX Generator - Convert course timelines into clean MDX course content
Uses OpenAI o3 to create beautiful, user-friendly course documentation
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class MDXGenerator:
    """Generate clean MDX course content from timeline data"""
    
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
    
    def generate_course_mdx(
        self,
        course_data: Dict[str, Any],
        timeline_data: Dict[str, Any],
        product_context: Dict[str, Any],
        max_tokens: int = 16000
    ) -> str:
        """
        Generate clean MDX content for a course.
        
        Args:
            course_data: The educational course definition from demo_generator
            timeline_data: The execution timeline with agent reasoning
            product_context: Product exploration data for context
            max_tokens: Max output tokens for o3 model
        
        Returns:
            Clean MDX content string
        """
        
        print(f"\n🎨 Generating MDX for: {course_data.get('title', 'Course')}")
        print(f"   Timeline steps: {len(timeline_data.get('events', []))}")
        print(f"   Using o3-mini model (max {max_tokens} tokens)\n")
        
        # Build the prompt
        prompt = self._build_mdx_prompt(course_data, timeline_data, product_context)
        
        try:
            # Call o3 model
            response = self.client.chat.completions.create(
                model="o3-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical writer who creates beautiful, clean MDX course content. You write clear, simple tutorials that guide users step-by-step with screenshots and explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=max_tokens
            )
            
            # Get the response
            mdx_content = response.choices[0].message.content
            
            # Handle code blocks (LLM often wraps in ```)
            mdx_content = self._extract_from_code_blocks(mdx_content)
            
            print(f"   ✅ Generated {len(mdx_content)} characters")
            print(f"   📊 Tokens used: {response.usage.total_tokens}")
            
            return mdx_content
            
        except Exception as e:
            print(f"   ❌ MDX generation failed: {e}")
            raise
    
    def _build_mdx_prompt(
        self,
        course_data: Dict[str, Any],
        timeline_data: Dict[str, Any],
        product_context: Dict[str, Any]
    ) -> str:
        """Build the prompt for MDX generation."""
        
        # Extract key information
        course_title = course_data.get('title', 'Course')
        key_idea = course_data.get('key_idea', '')
        target_user = course_data.get('target_user', '')
        difficulty = course_data.get('difficulty_level', '')
        estimated_time = course_data.get('estimated_time_minutes', 0)
        real_world_use_case = course_data.get('real_world_use_case', '')
        
        # Get product info
        product_name = product_context.get('product_name', 'the product')
        product_overview = product_context.get('product_overview', '')
        
        # Get timeline events
        events = timeline_data.get('events', [])
        recording_url = timeline_data.get('recording_url', '')
        
        # Build timeline summary
        timeline_summary = []
        for event in events:
            timeline_summary.append({
                'step': event.get('step_number'),
                'time': event.get('t_formatted'),
                'url': event.get('url', ''),
                'memory': event.get('memory', ''),
                'actions': event.get('actions', []),
                'screenshot': event.get('screenshot_url', '')
            })
        
        prompt = f"""Create a clean, beautiful MDX course file for this tutorial.

PRODUCT CONTEXT:
{product_name}
{product_overview[:500]}

COURSE INFORMATION:
Title: {course_title}
Target Audience: {target_user}
Difficulty: {difficulty}
Estimated Time: {estimated_time} minutes
Key Learning Objective: {key_idea}
Real-World Use Case: {real_world_use_case}

EXECUTION TIMELINE (What Actually Happened):
Total Steps: {len(events)}
Recording URL: {recording_url}

Timeline Events:
{json.dumps(timeline_summary, indent=2)[:8000]}

REQUIREMENTS:

1. OUTPUT FORMAT:
   - Valid MDX (markdown with JSX)
   - Clean, professional formatting
   - User-friendly language (not technical jargon)
   - Simple and clear explanations

2. STRUCTURE:
   - Course title and metadata
   - Introduction with use case
   - Step-by-step walkthrough
   - Each step should have:
     * Clear heading with timestamp
     * What to do (simple instructions)
     * Screenshot image (use actual screenshot URLs from timeline)
     * Why this step matters (brief explanation)
   - Conclusion with next steps

3. CONTENT GUIDELINES:
   - Write for the TARGET AUDIENCE ({target_user})
   - Keep it SIMPLE - avoid complexity
   - Use ACTUAL screenshots from the timeline
   - Reference EXACT URLs and actions from the execution
   - Make it ACTIONABLE - users should be able to follow along
   - Show the CONTEXT - explain how steps connect
   - Be ENCOURAGING - positive, supportive tone

4. SCREENSHOTS:
   - Use the actual screenshot URLs from the timeline
   - Format as: ![Step description](screenshot_url)
   - Include for EVERY major step
   - Add descriptive alt text

5. STYLE:
   - Friendly, conversational tone
   - Short paragraphs (2-3 sentences)
   - Bullet points for lists
   - Headers for sections
   - Emphasis for important points

6. MDX COMPONENTS (optional):
   - <Callout> for important notes
   - <Steps> for numbered sequences
   - <Card> for tips/warnings

IMPORTANT:
- Base the walkthrough on the ACTUAL execution timeline
- Use the agent's "memory" field to understand what happened
- Reference the screenshots that were captured
- Make it flow logically from step to step
- Keep it concise but complete
- The agent may or may not have gotten sidetracked or had to do other clicks. Understand exactly what the course is trying to show and present the ideal flow, skipping errors or going off track.

Generate a beautiful, clean MDX file that teaches users how to complete this course.
Output ONLY the MDX content, nothing else. Do NOT wrap it in code blocks or add any preamble.
Start directly with the MDX frontmatter or title.
"""
        
        return prompt
    
    def _extract_from_code_blocks(self, content: str) -> str:
        """Extract MDX from code blocks if LLM wraps it."""
        
        # Check if wrapped in ```mdx or ```markdown
        code_block_pattern = r'```(?:mdx|markdown)?\s*\n(.*?)\n```'
        matches = re.findall(code_block_pattern, content, re.DOTALL)
        
        if matches:
            # Return the content from code block
            return matches[0].strip()
        
        # Check for single ``` wrapping
        if content.strip().startswith('```') and content.strip().endswith('```'):
            # Remove first and last lines
            lines = content.strip().split('\n')
            return '\n'.join(lines[1:-1]).strip()
        
        # Return as-is if no code blocks
        return content.strip()
    
    def save_course_mdx(
        self,
        mdx_content: str,
        course_index: int,
        course_title: str,
        output_dir: Path
    ) -> str:
        """Save MDX content to file."""
        
        # Create safe filename from title
        safe_title = re.sub(r'[^a-z0-9]+', '-', course_title.lower())
        safe_title = safe_title.strip('-')[:50]  # Limit length
        
        filename = output_dir / f"course_{course_index + 1}_{safe_title}.mdx"
        
        with open(filename, 'w') as f:
            f.write(mdx_content)
        
        print(f"   💾 MDX saved: {filename.name}")
        
        return str(filename)
    
    def generate_all_course_mdx(
        self,
        demos_data: Dict[str, Any],
        execution_results: List[Dict[str, Any]],
        product_context: Dict[str, Any],
        output_dir: Path
    ) -> List[str]:
        """Generate MDX files for all executed courses."""
        
        print("\n" + "="*80)
        print("🎨 MDX GENERATION - Creating Clean Course Content")
        print("="*80)
        print(f"Product: {product_context.get('product_name', 'Unknown')}")
        print(f"Courses to generate: {len(execution_results)}")
        print("="*80 + "\n")
        
        mdx_files = []
        demos = demos_data.get('demos', [])
        
        for result in execution_results:
            if not isinstance(result, dict):
                continue
            
            course_idx = result.get('course_index', 0)
            
            # Skip if failed
            if result.get('status') != 'finished':
                print(f"⏭️  Skipping course {course_idx + 1} (status: {result.get('status')})")
                continue
            
            # Get course definition
            if course_idx >= len(demos):
                print(f"⚠️  Course {course_idx + 1} not found in demos")
                continue
            
            course_data = demos[course_idx]
            
            # Load timeline data
            timeline_file = result.get('timeline_file')
            if not timeline_file or not Path(timeline_file).exists():
                print(f"⚠️  Timeline file not found for course {course_idx + 1}")
                continue
            
            with open(timeline_file) as f:
                timeline_data = json.load(f)
            
            # Generate MDX
            try:
                mdx_content = self.generate_course_mdx(
                    course_data,
                    timeline_data,
                    product_context
                )
                
                # Save MDX
                mdx_file = self.save_course_mdx(
                    mdx_content,
                    course_idx,
                    course_data.get('title', f'Course {course_idx + 1}'),
                    output_dir
                )
                
                mdx_files.append(mdx_file)
                
            except Exception as e:
                print(f"   ❌ Failed to generate MDX for course {course_idx + 1}: {e}")
        
        print("\n" + "="*80)
        print(f"✅ MDX GENERATION COMPLETE")
        print("="*80)
        print(f"Generated {len(mdx_files)} MDX files")
        for mdx_file in mdx_files:
            print(f"  - {Path(mdx_file).name}")
        print("="*80 + "\n")
        
        return mdx_files


async def main():
    """Test MDX generator."""
    import sys
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ OPENAI_API_KEY not found")
        return
    
    # Load latest execution results
    outputs_dir = Path('outputs')
    
    # Find latest execution file
    execution_files = sorted(outputs_dir.glob('course_executions_*.json'))
    if not execution_files:
        print("❌ No execution files found. Run course executor first.")
        return
    
    latest_execution = execution_files[-1]
    print(f"📂 Loading execution: {latest_execution.name}\n")
    
    with open(latest_execution) as f:
        execution_data = json.load(f)
    
    # Load corresponding demos
    product_url = execution_data.get('product_url', '')
    
    # Find demos file (should be recent)
    demo_files = sorted(outputs_dir.glob('demos_*.json'))
    if not demo_files:
        print("❌ No demo files found")
        return
    
    with open(demo_files[-1]) as f:
        demos_data = json.load(f)
    
    # Load exploration for product context
    exploration_files = sorted(outputs_dir.glob('exploration_*.json'))
    product_context = {}
    
    if exploration_files:
        with open(exploration_files[-1]) as f:
            exploration = json.load(f)
            
            product_context = {
                'product_name': demos_data.get('product_name', ''),
                'product_url': exploration.get('product_url', ''),
                'product_overview': exploration.get('raw_analysis', '')[:1000]
            }
    
    # Generate MDX
    generator = MDXGenerator(openai_api_key=openai_key)
    
    # Limit courses if specified
    results = execution_data.get('executions', [])
    if len(sys.argv) > 1:
        max_courses = int(sys.argv[1])
        results = results[:max_courses]
        print(f"⚠️  Limiting to first {max_courses} courses\n")
    
    mdx_files = generator.generate_all_course_mdx(
        demos_data,
        results,
        product_context,
        outputs_dir
    )
    
    print(f"✅ Generated {len(mdx_files)} MDX course files!")
    print("\nTo view:")
    for mdx_file in mdx_files:
        print(f"  cat '{mdx_file}'")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

