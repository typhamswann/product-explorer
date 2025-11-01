# Educational Demo Generation 🎓

Automatically generate realistic educational demos and courses from product explorations using OpenAI's o3 model with structured outputs.

## What It Does

After exploring a product, the demo generator:
1. Analyzes the exploration results
2. Creates 5 progressive educational demos (beginner → advanced)
3. Generates specific UI instructions using actual elements from the exploration
4. Creates realistic use cases and scenarios
5. Outputs structured educational content

## How It Works

### Technology Stack

- **OpenAI o3-mini** - Advanced reasoning model for educational content
- **Structured Outputs** - Ensures consistent, well-formatted demos
- **Pydantic Models** - Type-safe data structures for demos

### Generation Process

```
Product Exploration
       ↓
Extract Features & UI Elements
       ↓
OpenAI o3 Analysis (16k max tokens)
       ↓
Structured Demo Generation
       ↓
5 Progressive Courses
```

## Output Structure

Each generated demo includes:

### 1. Course Metadata
- **Title**: Clear, engaging course name
- **Target Audience**: Who it's for (beginners, developers, etc.)
- **Difficulty Level**: Beginner, intermediate, or advanced
- **Estimated Time**: Minutes to complete
- **Key Learning Objective**: What you'll learn

### 2. Real-World Scenario
Realistic situation where someone would use this workflow

### 3. Key Concepts
Each concept includes:
- **Concept Name**: What it's called
- **Explanation**: Clear description in product context
- **Why Important**: Why users need to know this

### 4. Step-by-Step Implementation
- **Starting Point**: Exact page/location to begin
- **UI Steps**: Ordered list of actions with:
  - Step number
  - Specific action (using actual UI elements)
  - Expected result
  - Screen description
- **Expected Outcome**: What you'll accomplish
- **Common Pitfalls**: Mistakes to avoid

### 5. Next Steps
What to learn/do after completing this demo

## Example Demo Structure

```markdown
### Course 1: Creating Your First Workflow

**Target Audience:** Beginners
**Difficulty:** Beginner
**Estimated Time:** 15 minutes

#### 🎯 Key Learning Objective
Learn to navigate the dashboard and create your first workflow.

#### 🌍 Real-World Scenario
A small business owner prototyping an automation tool.

#### 📚 Key Concepts
1. **Dashboard Navigation**
   - Understanding core features from the home page
   - *Why it matters:* Essential for efficient use

#### 🛠️ Step-by-Step Implementation
**Starting Point:** Logged-in Home Page

1. **Click the User Profile icon at top right**
   - Expected result: Dropdown menu appears
   - Screen: Profile icon with dropdown

2. **Select 'Products' from dropdown**
   - Expected result: Navigate to Products page
   - Screen: Products page with Create button

...
```

## Usage

### Automatic (Default)
```bash
python explore.py https://app.example.com
```
Demos are generated automatically after exploration.

### Skip Demo Generation
```bash
python explore.py https://app.example.com --no-demos
```

### Standalone Demo Generation
```python
from demo_generator import DemoGenerator

generator = DemoGenerator(openai_api_key="your_key")

# Load existing exploration
with open('exploration.json') as f:
    exploration_data = json.load(f)

# Generate demos
demos = generator.generate_demos(
    exploration_data=exploration_data,
    num_demos=5,
    max_tokens=16000
)

# Save results
generator.save_demos(demos, exploration_data, output_dir)
```

## Output Files

### Markdown Report (COURSES.md)
Human-readable educational content:
- Learning path overview
- Each course with full details
- Formatted for easy reading
- Ready for documentation/training

### JSON Data
Structured data including:
- All course metadata
- Concepts and implementations
- Full step-by-step instructions
- Programmatically accessible

## Demo Characteristics

### Progressive Learning
- **Beginner**: Essential workflows, core features
- **Intermediate**: Combined features, complex workflows
- **Advanced**: Power user features, integrations

### Realistic Scenarios
Every demo includes a real-world use case:
- "A freelancer managing client projects"
- "A team automating reporting workflows"
- "A developer building API integrations"

### Specific UI Instructions
All steps use actual UI elements from exploration:
- "Click the blue 'Create' button in top-right"
- "Navigate to Settings → API Keys"
- "Select 'Advanced' from the dropdown menu"

### Educational Focus
Teaches concepts, not just clicking:
- WHY each step matters
- HOW features connect
- WHAT to learn next

## Token Usage

Typical usage per exploration:
- **Input**: ~2,500-3,500 tokens (exploration analysis)
- **Output**: ~4,000-5,000 tokens (5 detailed demos)
- **Total**: ~7,000-8,500 tokens per generation

With o3-mini pricing, this costs approximately $0.03-0.04 per exploration.

## Quality Assurance

The structured output ensures:
- ✅ All required fields present
- ✅ Consistent formatting
- ✅ Valid JSON structure
- ✅ Type-safe data
- ✅ No hallucinated field names

## Customization

Edit `demo_generator.py` to customize:

### Number of Demos
```python
demos = generator.generate_demos(
    exploration_data=data,
    num_demos=10,  # Generate 10 demos instead of 5
    max_tokens=16000
)
```

### Max Tokens
```python
demos = generator.generate_demos(
    exploration_data=data,
    num_demos=5,
    max_tokens=24000  # More detailed demos
)
```

### Prompt Modification
Edit the `_build_demo_prompt()` method to:
- Change demo style
- Add specific requirements
- Target different audiences
- Include additional context

## Example Results (Spinstack)

Generated 5 courses covering:
1. **Creating First Agent Flow** (Beginner, 15 min)
   - Dashboard navigation
   - Natural language workflow creation

2. **Customizing Agent Flows** (Intermediate, 20 min)
   - Visual workflow editor
   - Configuration and testing

3. **Account Management** (Beginner, 10 min)
   - Settings navigation
   - Subscription handling

4. **External API Integration** (Advanced, 30 min)
   - API key management
   - Complex integrations

5. **Production Deployment** (Advanced, 25 min)
   - Publishing workflows
   - Monitoring and optimization

## Benefits

### For Product Teams
- Generate onboarding content automatically
- Create consistent documentation
- Scale tutorial creation
- Reduce manual writing time

### For Users
- Clear, step-by-step guidance
- Realistic scenarios
- Progressive learning path
- Specific UI instructions

### For Developers
- Structured data format
- Programmatic access
- Type-safe models
- Easy integration

## Tips for Best Results

1. **Thorough Exploration**: Better exploration = better demos
2. **Complete Features**: Explore all major features for comprehensive demos
3. **Specific Actions**: The more specific the exploration, the more specific the demos
4. **Review Output**: Generated demos are great starting points for refinement

## Limitations

- Demos are generated from exploration data only
- May miss features not discovered during exploration
- Quality depends on exploration thoroughness
- Some product-specific nuances may need manual editing

## Future Enhancements

Potential improvements:
- Screenshots/videos generation
- Interactive tutorial format
- Multiple difficulty tracks
- Language localization
- Custom demo templates
- A/B testing variants

---

**The demo generator transforms raw exploration into production-ready educational content! 🚀**

