# MDX Course Generation - Production-Ready Documentation 🎨

## Overview

The final step in the pipeline: Transform raw timeline data into beautiful, clean MDX files ready for documentation sites.

## What It Does

Uses OpenAI o3-mini to convert:
- Product exploration context
- Educational course definitions
- Execution timeline with agent reasoning
- Screenshots and timestamps

Into: **Clean, user-friendly MDX course content**

## Pipeline Stage 4

```
Stage 1: Explore → Product analysis
Stage 2: Generate → Educational courses  
Stage 3: Execute → Parallel recording + timelines
Stage 4: MDX     → Clean documentation (NEW!)
```

## MDX Output Features

### Frontmatter
```yaml
---
title: "Demo 1: Kickstart Your First Agent Flow"
difficulty: Beginner
estimatedTime: "15 minutes"
audience: "Beginners exploring AI automation"
product: SpinStack
category: "AI/Agentic Workflow Automation"
url: "https://www.spinstack.dev/"
---
```

### Course Structure
- User-friendly title and introduction
- Clear step-by-step walkthrough
- Screenshots for every major step
- Timestamps (e.g., [00:06])
- "What to do" instructions
- "Why this matters" explanations
- Conclusion with next steps
- MDX components (<Callout>, etc.)

### Example Step
```mdx
## Step 3: Open Your User Profile Menu (00:15)

**What to do:**  
- Once logged in, locate and click the User Profile icon at the top right.

**Screenshot:**  
![User Profile icon clicked](https://cdn.browser-use.com/screenshots/.../3.png)

**Why this matters:**  
Accessing the user profile reveals crucial navigation options.
```

## Generated Content Quality

### Language
- ✅ Simple, conversational tone
- ✅ Non-technical (suitable for beginners)
- ✅ Encouraging and supportive
- ✅ Action-oriented instructions

### Structure
- ✅ Logical flow from step to step
- ✅ Clear headings with timestamps
- ✅ Consistent formatting
- ✅ Proper MDX syntax

### Visuals
- ✅ Screenshots from actual execution
- ✅ Descriptive alt text
- ✅ Embedded at right moments
- ✅ CDN-hosted (no local files)

### Content
- ✅ Based on real execution
- ✅ Uses timeline data accurately
- ✅ Contextual explanations
- ✅ Connects to product purpose

## Usage

### Automatic (Integrated Pipeline)
```bash
python explore.py https://www.spinstack.dev/ --execute-courses
```

MDX generation happens automatically after course execution.

### Standalone
```bash
python mdx_generator.py [max_courses]

# Examples:
python mdx_generator.py 1  # Generate MDX for first course
python mdx_generator.py 5  # Generate MDX for all 5 courses
```

## Input Data

The MDX generator uses three data sources:

### 1. Product Context
```python
{
  'product_name': 'SpinStack',
  'product_url': 'https://www.spinstack.dev/',
  'product_overview': '...'
}
```

### 2. Course Definition
```python
{
  'title': 'Kickstart Your First Agent Flow',
  'key_idea': '...',
  'target_user': 'Beginners',
  'difficulty_level': 'beginner',
  'real_world_use_case': '...'
}
```

### 3. Execution Timeline
```python
{
  'events': [
    {
      'step_number': 1,
      't_formatted': '00:06',
      'url': '...',
      'memory': 'Agent reasoning...',
      'actions': [...],
      'screenshot_url': '...'
    },
    ...
  ]
}
```

## Output Files

### Per Course MDX File
```
course_{N}_{safe-title}.mdx
```

Example: `course_1_demo-1-kickstart-your-first-agent-flow.mdx`

**File Size:** 5-15 KB per course  
**Content:** Production-ready MDX  
**Ready For:** Documentation sites, LMS platforms, help centers

## Technical Implementation

### LLM Processing
```python
response = openai.chat.completions.create(
    model="o3-mini",
    messages=[
        {"role": "system", "content": "Expert technical writer..."},
        {"role": "user", "content": detailed_prompt}
    ],
    max_completion_tokens=16000
)

mdx_content = response.choices[0].message.content
```

### Code Block Handling
The LLM sometimes wraps MDX in triple backticks:

````
```mdx
---
title: "Course"
---
# Content
```
````

**Solution:** Automatic extraction:
```python
def _extract_from_code_blocks(content):
    # Remove ```mdx or ```markdown wrappers
    pattern = r'```(?:mdx|markdown)?\s*\n(.*?)\n```'
    matches = re.findall(pattern, content, re.DOTALL)
    return matches[0] if matches else content
```

### Filename Generation
```python
# Convert title to safe filename
title = "Demo 1: Kickstart Your First Agent Flow"
safe = "demo-1-kickstart-your-first-agent-flow"

filename = f"course_1_{safe}.mdx"
```

## Prompt Engineering

The prompt is highly specific:

### Key Instructions
1. **Format**: Valid MDX with frontmatter
2. **Language**: Simple, user-friendly
3. **Structure**: Title → Intro → Steps → Conclusion
4. **Screenshots**: Use actual URLs from timeline
5. **Timestamps**: Include for navigation
6. **Context**: Explain why each step matters
7. **Tone**: Friendly, encouraging

### What Makes It Work
- Provides complete context (product + course + timeline)
- Shows actual execution data
- Specifies exact output format
- Includes target audience
- Emphasizes simplicity and clarity

## Real Example Output

### Input
- Product: SpinStack (AI workflow automation)
- Course: "Kickstart Your First Agent Flow"
- Timeline: 8 steps, 62 seconds
- Screenshots: 8 images

### Output MDX
- Clean frontmatter
- Welcoming introduction
- 8 steps with screenshots
- Timestamps: [00:06], [00:11], etc.
- Encouraging conclusion
- MDX components used
- 5,250 characters

**Quality:** Production-ready!

## Integration Points

### Documentation Sites
- Next.js MDX
- Docusaurus
- GitBook
- MkDocs Material

### LMS Platforms
- Teachable
- Thinkific
- Custom learning platforms

### Help Centers
- Intercom Articles
- Zendesk Guide
- Notion docs

## MDX Components Used

### Callout (Info Boxes)
```mdx
<Callout type="info">
  In this demo, you'll follow 8 simple steps.
</Callout>

<Callout type="success">
  Great job! Keep experimenting.
</Callout>
```

### Steps (Optional)
Could be extended to use:
```mdx
<Steps>
  ### Step 1
  Content...
  
  ### Step 2
  Content...
</Steps>
```

### Cards (Optional)
For tips and warnings:
```mdx
<Card title="Pro Tip">
  Use keyboard shortcuts to speed up your workflow.
</Card>
```

## Token Usage

### Typical Course
- Input tokens: ~2,000-3,000 (context + timeline)
- Output tokens: ~3,000-5,000 (MDX content)
- Total: ~5,000-8,000 tokens

### Cost (o3-mini)
- Per course: ~$0.02-0.03
- For 5 courses: ~$0.10-0.15

## Quality Characteristics

### Content Quality
- ✅ Accurate (based on real execution)
- ✅ Complete (all steps covered)
- ✅ Clear (simple language)
- ✅ Contextual (explains why)

### Technical Quality
- ✅ Valid MDX syntax
- ✅ Proper frontmatter
- ✅ Working image links
- ✅ Clean formatting

### User Experience
- ✅ Easy to follow
- ✅ Well-structured
- ✅ Visually appealing (with screenshots)
- ✅ Encouraging tone

## Customization

### Adjust Output Style
Edit the system prompt in `mdx_generator.py`:
```python
messages=[
    {
        "role": "system",
        "content": "You are [CUSTOM STYLE]. You write [CUSTOM APPROACH]..."
    },
    ...
]
```

### Change MDX Components
Update the prompt to use different components:
- Custom component syntax
- Different callout types
- Platform-specific features

### Modify Structure
Adjust prompt requirements:
- Add/remove sections
- Change step format
- Include additional metadata

## Benefits

### For Product Teams
- Instant documentation generation
- Consistent formatting across courses
- Ready for publishing
- Scalable to any number of products

### For Users
- Clear, easy-to-follow tutorials
- Visual guidance with screenshots
- Contextual explanations
- Progressive learning path

### For Developers
- Valid MDX output
- No manual formatting needed
- Easy integration with doc sites
- Automated content pipeline

## Example Use Case

### Before
1. Record course manually
2. Take screenshots
3. Write tutorial (hours)
4. Format for docs
5. Upload images
6. Review and edit

**Time:** Days

### After
1. Run pipeline: `python explore.py <url> --execute-courses`
2. Get MDX files automatically
3. Copy to docs repo

**Time:** ~6 minutes + copy

**Savings:** 100x faster!

## File Naming Convention

```
course_{index}_{safe-title}.mdx

Examples:
- course_1_demo-1-kickstart-your-first-agent-flow.mdx
- course_2_demo-2-customizing-and-configuring-your-agent-flow.mdx
- course_3_demo-3-managing-your-account-settings.mdx
```

## Complete Output Per Course

```
outputs/
├── course_1_*_timeline.json          ← Raw timeline data
├── course_1_*_SCRIPT.md              ← Enhanced script
├── course_1_kickstart-flow.mdx       ← Clean MDX (NEW!)
└── Recording URL                      ← Browser replay
```

## Testing

### Run Standalone
```bash
cd explore_product
python mdx_generator.py 1
```

### Run Integrated
```bash
python explore.py https://www.spinstack.dev/ --execute-courses
```

### Verify Output
```bash
# View generated MDX
cat outputs/course_1_*.mdx

# Copy to docs site
cp outputs/course_*.mdx ../docs/courses/
```

## Future Enhancements

### Potential Improvements
1. **Interactive demos** - Add code playgrounds
2. **Video embeds** - Include recording inline
3. **Quizzes** - Add comprehension checks
4. **Related courses** - Link to next/previous
5. **Code examples** - Extract from execution
6. **Search optimization** - Add SEO metadata
7. **Localization** - Multi-language support

---

**From raw timeline data to production-ready MDX documentation! 🎨**

