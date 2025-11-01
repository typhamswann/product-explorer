"""
Demo Generator - Creates educational demos from product explorations
Uses OpenAI Structured Outputs to generate realistic, helpful courses
"""

import json
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI


# Pydantic models for structured output
class UIStep(BaseModel):
    """A specific UI interaction step"""
    step_number: int = Field(description="The sequence number of this step")
    action: str = Field(description="The specific UI action to take (e.g., 'Click the Create button in top-right')")
    expected_result: str = Field(description="What should happen after this action")
    screenshot_description: str = Field(description="Description of what the screen should look like")


class DemoConcept(BaseModel):
    """A key concept that this demo teaches"""
    concept_name: str = Field(description="Name of the concept")
    explanation: str = Field(description="Clear explanation of the concept in context of the product")
    why_important: str = Field(description="Why this concept matters to users")


class DemoImplementation(BaseModel):
    """Detailed implementation plan for a demo"""
    starting_point: str = Field(description="Where in the product to start (specific page/view)")
    ui_steps: List[UIStep] = Field(description="Ordered list of UI steps to complete the demo")
    expected_outcome: str = Field(description="What the user will have accomplished")
    common_pitfalls: List[str] = Field(description="Common mistakes to avoid")


class EducationalDemo(BaseModel):
    """A complete educational demo/course"""
    title: str = Field(description="Clear, engaging title for the demo")
    key_idea: str = Field(description="The main learning objective - what this demo teaches")
    target_user: str = Field(description="Who this demo is for (e.g., 'beginners', 'developers', 'data analysts')")
    difficulty_level: str = Field(description="Difficulty: beginner, intermediate, or advanced")
    estimated_time_minutes: int = Field(description="Estimated time to complete in minutes")
    concepts: List[DemoConcept] = Field(description="Key concepts this demo teaches")
    implementation: DemoImplementation = Field(description="Step-by-step implementation plan")
    real_world_use_case: str = Field(description="A realistic scenario where someone would use this")
    next_steps: List[str] = Field(description="What to learn/do after completing this demo")


class DemoCollection(BaseModel):
    """Collection of educational demos for a product"""
    product_name: str = Field(description="Name of the product")
    product_category: str = Field(description="Category/type of product")
    learning_path_overview: str = Field(description="Overview of how these demos build on each other")
    demos: List[EducationalDemo] = Field(
        description="List of educational demos, ordered from beginner to advanced"
    )


class DemoGenerator:
    """Generate educational demos from product exploration data"""
    
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
    
    def generate_demos(
        self,
        exploration_data: dict,
        num_demos: int = 5,
        max_tokens: int = 16000
    ) -> DemoCollection:
        """
        Generate educational demos based on product exploration.
        
        Args:
            exploration_data: The exploration results from ProductExplorer
            num_demos: Number of demos to generate (default: 5)
            max_tokens: Max output tokens for o3 model (default: 16000)
        
        Returns:
            DemoCollection with structured educational demos
        """
        
        print("\n" + "="*80)
        print("🎓 GENERATING EDUCATIONAL DEMOS")
        print("="*80)
        print(f"Product: {exploration_data.get('product_url')}")
        print(f"Target demos: {num_demos}")
        print(f"Using: o3 model with structured outputs")
        print("="*80 + "\n")
        
        # Extract relevant information from exploration
        analysis = exploration_data.get('analysis', {})
        raw_output = analysis.get('raw_output', exploration_data.get('raw_analysis', ''))
        product_url = exploration_data.get('product_url', '')
        
        # Build the prompt
        prompt = self._build_demo_prompt(raw_output, product_url, num_demos)
        
        print("🤖 Calling OpenAI o3 with structured output mode...")
        print(f"   Max output tokens: {max_tokens}")
        print(f"   Requesting {num_demos} demos\n")
        
        try:
            # Use structured output with o3 model
            response = self.client.chat.completions.parse(
                model="o3-mini",  # o3 with structured outputs
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational content designer who creates practical, engaging tutorials for software products. You create realistic, helpful demo courses that teach users how to effectively use products."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format=DemoCollection,
                max_completion_tokens=max_tokens
                # Note: o3 models don't support temperature parameter
            )
            
            # Check for refusal
            if response.choices[0].message.refusal:
                print(f"❌ Model refused: {response.choices[0].message.refusal}")
                raise ValueError(f"Model refused to generate demos: {response.choices[0].message.refusal}")
            
            # Get parsed result
            demo_collection = response.choices[0].message.parsed
            
            print(f"✅ Generated {len(demo_collection.demos)} educational demos!")
            print(f"   Tokens used: {response.usage.total_tokens}")
            print(f"   Input: {response.usage.prompt_tokens}, Output: {response.usage.completion_tokens}\n")
            
            return demo_collection
            
        except Exception as e:
            print(f"❌ Error generating demos: {e}")
            raise
    
    def _build_demo_prompt(self, exploration_output: str, product_url: str, num_demos: int) -> str:
        """Build the prompt for demo generation"""
        
        prompt = f"""Based on the following product exploration, create {num_demos} educational demos/courses that will help users learn to use this product effectively.

PRODUCT URL: {product_url}

EXPLORATION RESULTS:
{exploration_output}

REQUIREMENTS:

1. Create {num_demos} demos that build on each other (beginner → advanced)
2. Each demo should be REALISTIC and PRACTICAL - something users would actually do
3. Use SPECIFIC UI INSTRUCTIONS from the exploration (exact button names, page locations, etc.)
4. Make demos ACTIONABLE - someone should be able to follow step-by-step
5. Focus on teaching CONCEPTS, not just clicking buttons
6. Include realistic use cases and examples

DEMO GUIDELINES:

- **Beginner demos**: Start with essential workflows, core features
- **Intermediate demos**: Combine features, more complex workflows
- **Advanced demos**: Power user features, integrations, optimization

For each demo:
- Use actual UI elements mentioned in the exploration
- Reference specific pages, buttons, menus from the analysis
- Create realistic scenarios (e.g., "Build a project tracker" not just "Create a project")
- Explain WHY each step matters
- Include common pitfalls users might encounter

ENSURE DIVERSITY:
- Cover different aspects of the product
- Target different user personas (beginners, developers, teams, etc.)
- Show different use cases and workflows
- Progress from simple to complex

Generate a comprehensive learning path with {num_demos} well-structured educational demos.
"""
        
        return prompt
    
    def save_demos(
        self,
        demo_collection: DemoCollection,
        exploration_data: dict,
        output_dir: Path
    ) -> dict:
        """
        Save generated demos to files.
        
        Returns:
            Dictionary with paths to saved files
        """
        
        from datetime import datetime
        from urllib.parse import urlparse
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        domain = urlparse(exploration_data['product_url']).netloc.replace('.', '_')
        
        # Save JSON (structured data)
        json_file = output_dir / f"demos_{domain}_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(demo_collection.model_dump(), f, indent=2)
        
        # Save human-readable markdown
        md_file = output_dir / f"demos_{domain}_{timestamp}_COURSES.md"
        with open(md_file, 'w') as f:
            self._write_markdown_report(f, demo_collection, exploration_data)
        
        print(f"💾 Demos saved:")
        print(f"   JSON: {json_file}")
        print(f"   Markdown: {md_file}\n")
        
        return {
            'json': str(json_file),
            'markdown': str(md_file)
        }
    
    def _write_markdown_report(self, f, demo_collection: DemoCollection, exploration_data: dict):
        """Write human-readable markdown report"""
        
        f.write("# Educational Demos & Courses\n\n")
        f.write(f"**Product:** {demo_collection.product_name}\n")
        f.write(f"**Category:** {demo_collection.product_category}\n")
        f.write(f"**URL:** {exploration_data.get('product_url')}\n")
        f.write(f"**Generated:** {exploration_data.get('timestamp')}\n\n")
        
        f.write("---\n\n")
        f.write("## Learning Path Overview\n\n")
        f.write(f"{demo_collection.learning_path_overview}\n\n")
        
        f.write("---\n\n")
        f.write(f"## Courses ({len(demo_collection.demos)} Total)\n\n")
        
        for i, demo in enumerate(demo_collection.demos, 1):
            f.write(f"### Course {i}: {demo.title}\n\n")
            
            # Metadata
            f.write(f"**Target Audience:** {demo.target_user}\n")
            f.write(f"**Difficulty:** {demo.difficulty_level.title()}\n")
            f.write(f"**Estimated Time:** {demo.estimated_time_minutes} minutes\n\n")
            
            # Key idea
            f.write(f"#### 🎯 Key Learning Objective\n\n")
            f.write(f"{demo.key_idea}\n\n")
            
            # Real-world use case
            f.write(f"#### 🌍 Real-World Scenario\n\n")
            f.write(f"{demo.real_world_use_case}\n\n")
            
            # Concepts
            f.write(f"#### 📚 Key Concepts\n\n")
            for j, concept in enumerate(demo.concepts, 1):
                f.write(f"{j}. **{concept.concept_name}**\n")
                f.write(f"   - {concept.explanation}\n")
                f.write(f"   - *Why it matters:* {concept.why_important}\n\n")
            
            # Implementation steps
            f.write(f"#### 🛠️ Step-by-Step Implementation\n\n")
            f.write(f"**Starting Point:** {demo.implementation.starting_point}\n\n")
            
            for step in demo.implementation.ui_steps:
                f.write(f"{step.step_number}. **{step.action}**\n")
                f.write(f"   - Expected result: {step.expected_result}\n")
                f.write(f"   - Screen: {step.screenshot_description}\n\n")
            
            # Expected outcome
            f.write(f"**✅ Expected Outcome**\n\n")
            f.write(f"{demo.implementation.expected_outcome}\n\n")
            
            # Common pitfalls
            if demo.implementation.common_pitfalls:
                f.write(f"**⚠️ Common Pitfalls to Avoid**\n\n")
                for pitfall in demo.implementation.common_pitfalls:
                    f.write(f"- {pitfall}\n")
                f.write("\n")
            
            # Next steps
            f.write(f"#### 🚀 Next Steps\n\n")
            f.write(f"After completing this demo, you should:\n\n")
            for next_step in demo.next_steps:
                f.write(f"- {next_step}\n")
            
            f.write(f"\n---\n\n")
        
        # Footer
        f.write("## Additional Resources\n\n")
        f.write(f"- **Test Account:** {exploration_data.get('temp_email')}\n")
        f.write(f"- **Password:** {exploration_data.get('password')}\n")
        if exploration_data.get('share_url'):
            f.write(f"- **Exploration Recording:** {exploration_data.get('share_url')}\n")


def main():
    """Test demo generation"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv(Path(__file__).parent.parent / '.env')
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ Error: OPENAI_API_KEY not found in .env")
        return
    
    # Load a sample exploration result
    outputs_dir = Path(__file__).parent / "outputs"
    
    # Find the most recent spinstack exploration
    exploration_files = sorted(outputs_dir.glob("exploration_www_spinstack_dev_*.json"))
    if not exploration_files:
        print("❌ No exploration files found. Run an exploration first.")
        return
    
    latest_file = exploration_files[-1]
    print(f"📂 Loading exploration: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        exploration_data = json.load(f)
    
    # Generate demos
    generator = DemoGenerator(openai_api_key=openai_key)
    
    try:
        demo_collection = generator.generate_demos(
            exploration_data=exploration_data,
            num_demos=5,
            max_tokens=16000
        )
        
        # Save results
        saved_files = generator.save_demos(
            demo_collection=demo_collection,
            exploration_data=exploration_data,
            output_dir=outputs_dir
        )
        
        print("="*80)
        print("✅ DEMO GENERATION COMPLETE!")
        print("="*80)
        print(f"Generated {len(demo_collection.demos)} educational demos")
        print(f"Markdown report: {saved_files['markdown']}")
        print(f"JSON data: {saved_files['json']}")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Demo generation failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

