# Product Explorer 🔍

Automated product exploration and documentation using AI browser automation. Give it any product URL, and it will sign up, explore thoroughly, and generate comprehensive documentation.

## What It Does

The Product Explorer:
1. **Automatically signs up** for the product using a temporary email
2. **Handles email verification** automatically (links or codes)
3. **Thoroughly explores** the product by navigating through all sections
4. **Documents everything** it finds in a structured format

## Output Deliverables

For each product explored, you'll get:

### 1. Product Description
- What the product is
- What problem it solves
- Who it's for
- Core purpose and value proposition

### 2. High-Level User Actions
For each action/feature discovered:
- **Action Name**: What the feature is called
- **How to Start**: Step-by-step instructions from the home page
- **What It Does**: Detailed explanation of the action and its effects
- **Purpose**: Why this action exists and how it serves the user

### 3. Additional Analysis
- Product workflow overview
- Unique observations
- Integration capabilities
- Target use cases

### 4. Educational Demos 🎓
**Automatically generated using OpenAI o3 model:**
- 5 progressive courses (beginner → advanced)
- Realistic use cases and scenarios
- Specific UI instructions from exploration
- Step-by-step implementation plans
- Key concepts and learning objectives
- Common pitfalls and next steps

See `DEMO_GENERATION.md` for details!

### 5. Course Executions & Timelines 🎬
**Parallel execution with timeline logging:**
- Execute all courses in parallel
- Unique email + session per course
- Timeline with timestamps and URLs
- Recording links for each course
- Credentials for manual verification

See `TIMELINE_LOGGING.md` and `COURSE_EXECUTION.md` for details!

### 6. Clean MDX Course Content 🎨
**Production-ready documentation:**
- Beautiful MDX files per course
- User-friendly, simple language
- Screenshots embedded from execution
- Timestamps for navigation
- Ready for Next.js, Docusaurus, etc.

See `MDX_GENERATION.md` for details!

### 7. Live Video Recording 🎥 (NEW!)
**Actual downloadable videos:**
- Records real live browser execution
- Smooth WebM video files (not screenshots!)
- 1280x720 resolution
- 1-3 MB per minute
- Playable offline, uploadable anywhere

See `LIVE_VIDEO_RECORDING.md` for details!

## Setup

### Prerequisites

You already have the main dependencies installed. The Product Explorer uses:
- `browser-use` - AI browser automation
- `agentmail` - Temporary email service
- `openai` - LLM for analysis
- `requests` - API calls
- `python-dotenv` - Environment variables

### API Keys

The tool uses your existing API keys from the main `.env` file:
- `AGENTMAIL_API_KEY` - For creating temporary emails
- `BROWSER_USE_API_KEY` - For browser automation
- `OPENAI_API_KEY` - For intelligent verification handling

These should already be configured in `/Users/typham-swann/Desktop/yc-hackathon/.env`

## Usage

### Basic Usage

```bash
cd explore_product
python explore.py <product_url>
```

This will:
- Explore the product
- Generate exploration report
- **Automatically generate 5 educational demos**

### Full Pipeline (with Course Execution)

```bash
python explore.py <product_url> --execute-courses
```

This will:
- Explore the product
- Generate 5 educational demos
- **Execute all 5 courses in parallel** ⬅️ NEW!
- **Create recordings with timelines** ⬅️ NEW!

### Skip Demo Generation

```bash
python explore.py <product_url> --no-demos
```

### Example

```bash
python explore.py https://app.example.com
```

### What Happens

1. **Session Creation**: Creates a browser session via Browser-Use Cloud
2. **Email Setup**: Generates a temporary email for signup
3. **Signup**: Navigates to the product and signs up automatically
4. **Verification**: Monitors email and handles verification (link or code)
5. **Exploration**: Thoroughly explores the product interface
6. **Analysis**: Documents all features and user actions
7. **Output**: Saves comprehensive report and structured JSON data

### Live Monitoring

When you run the exploration, you'll get a live URL to watch the browser in real-time:

```
📺 WATCH LIVE
================================================================================
https://cloud.browser-use.com/sessions/xyz123/live
================================================================================
```

Open this URL in your browser to see the AI exploring the product!

## Output Files

Results are saved in the `outputs/` directory:

### Report File (TXT)
```
exploration_example_com_20251101_120000_REPORT.txt
```

Human-readable report with:
- Product overview
- All discovered actions with descriptions
- Workflow analysis
- Test account credentials
- Recording link

### JSON Data
```
exploration_example_com_20251101_120000.json
```

Structured data including:
- Product URL
- Timestamp and duration
- Account credentials
- Session/task IDs
- Share URL for recording
- Parsed analysis data

### Educational Demos 🎓
```
demos_example_com_20251101_120000_COURSES.md
demos_example_com_20251101_120000.json
```

AI-generated educational content:
- 5 progressive courses with specific UI instructions
- Realistic scenarios and use cases
- Step-by-step implementation plans
- Key concepts and learning objectives
- Generated using OpenAI o3-mini model

### Course Executions & Timelines 🎬
```
course_executions_example_com_TIMESTAMP_REPORT.md
course_executions_example_com_TIMESTAMP.json
course_0_SESSION_ID_timeline.json
course_1_SESSION_ID_timeline.json
...
```

Parallel course execution with timeline logging:
- **Timeline JSON per course** - Event log with timestamps & URLs
- **Execution report** - All courses with timeline previews
- **Recording links** - Browser replay for each course
- **Credentials** - Email + password per course
- **Step-by-step events** - Navigate recordings precisely

### Clean MDX Files 🎨 (NEW!)
```
course_1_kickstart-your-first-agent-flow.mdx
course_2_customizing-agent-flows.mdx
course_3_account-management.mdx
...
```

Production-ready course documentation:
- **Valid MDX syntax** - Ready for doc sites
- **User-friendly content** - Simple, clear language
- **Screenshots embedded** - From actual execution
- **Timestamps included** - Navigate recordings
- **MDX components** - Callouts, emphasis, etc.

## Example Output

```
================================================================================
PRODUCT EXPLORATION REPORT
================================================================================

Product URL: https://app.example.com
Explored on: 2025-11-01T12:00:00
Duration: 245.3 seconds
Status: finished

🎥 Recording: https://cloud.browser-use.com/sessions/xyz/share

Test Account:
  Email: user123@agentmail.to
  Password: aBcD1234!@#$

================================================================================
ANALYSIS
================================================================================

## PRODUCT OVERVIEW

**Product Name:** Example App
**URL:** https://app.example.com
**Category:** Project Management

**What This Product Is:**
Example App is a collaborative project management platform designed for remote
teams. It provides task tracking, team communication, and progress visualization
in a unified interface...

## HIGH-LEVEL USER ACTIONS

### ACTION #1: Create New Project

**How to Start (from home page when logged in):**
1. Click the "Projects" tab in the left sidebar
2. Click the blue "New Project" button in the top right
3. A modal dialog will appear

**What This Action Does:**
Opens a project creation dialog where you can:
- Enter project name
- Set project description
- Choose project template (Agile, Waterfall, Custom)
- Assign team members
- Set deadline
Creates a new project workspace accessible to assigned team members.

**Purpose in the Product:**
Projects are the top-level organizational units. Creating a project establishes
a dedicated workspace for teams to collaborate on specific initiatives...

### ACTION #2: Invite Team Members
...

```

## Advanced Usage

### Programmatic Usage

You can also use the `ProductExplorer` class directly in Python:

```python
import asyncio
from product_explorer import ProductExplorer

async def main():
    explorer = ProductExplorer(
        agentmail_api_key="your_key",
        browser_use_api_key="your_key",
        openai_api_key="your_key",
        output_dir="./outputs"
    )
    
    result = await explorer.explore_product("https://app.example.com")
    print(f"Analysis saved to: {result['saved_files']['txt']}")

asyncio.run(main())
```

### Customizing the Exploration

Edit `product_explorer.py` to customize:
- Exploration depth (in `_build_exploration_task` method)
- Output format (in `_save_exploration` method)
- Verification timeout (in `get_verification_data` method)

## How It Works

### Architecture

1. **Browser-Use Cloud**: Provides remote browser automation
2. **AgentMail**: Supplies temporary email for signups
3. **OpenAI GPT-4o**: Extracts verification links from emails
4. **LLM Agent**: Intelligently navigates and explores the product

### Exploration Strategy

The agent is instructed to:
- Navigate through ALL major sections
- Click into different pages and views
- Try creating test items/projects
- Look for hidden features and keyboard shortcuts
- Document the navigation path for each action
- Explain the purpose of each feature in context

### Email Verification Flow

1. Agent submits signup form
2. Background task monitors AgentMail inbox
3. When verification email arrives:
   - GPT-4o extracts the verification link/code
   - If link: Creates new session at that URL
   - If code: Displays for agent to enter
4. Agent continues exploration after verification

## Troubleshooting

### "Missing API keys" Error

Make sure your `.env` file in the parent directory contains:
```
AGENTMAIL_API_KEY=your_key_here
BROWSER_USE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

### "Rate limit hit" Warning

The tool automatically retries with exponential backoff. Just wait for it to retry.

### Session Stops Early

Some products may have aggressive security. Check the recording URL to see what happened.

### No Actions Found

Some products may require more extensive exploration. The agent tries to be thorough but may miss features behind non-obvious UI elements.

## Directory Structure

```
explore_product/
├── README.md              # This file
├── explore.py            # CLI interface
├── product_explorer.py   # Main exploration logic
└── outputs/              # Generated reports and data
    ├── exploration_*.json
    └── exploration_*_REPORT.txt
```

## Tips for Best Results

1. **Use products with clear signup flows** - The agent works best with standard signup forms
2. **Allow time for thorough exploration** - Complex products may take 5-10 minutes to explore fully
3. **Watch the live session** - The live URL lets you see what the agent is doing
4. **Review the recording** - If results seem incomplete, watch the recording to see where the agent went

## Standalone Design

This tool is completely self-contained:
- ✅ No dependencies on other project files
- ✅ Uses shared `.env` for API keys
- ✅ Can be moved to another directory
- ✅ Terminal-only interface
- ✅ All outputs saved to local files

## Examples

### Explore a SaaS Product
```bash
python explore.py https://app.notion.so
```

### Explore an E-commerce Platform
```bash
python explore.py https://shopify.com
```

### Explore a Development Tool
```bash
python explore.py https://github.com
```

## Output Format Summary

Each exploration generates:

📄 **TXT Report** - Human-readable analysis
- Product overview and purpose
- Step-by-step action guides
- Workflow explanation
- Test account details

📊 **JSON Data** - Structured information
- Programmatic access to analysis
- Session metadata
- Timestamps and status
- Recording URLs

🎥 **Browser Recording** - Visual replay
- Watch the entire exploration
- See exactly what the agent did
- Debug any issues

## Next Steps

After running an exploration:

1. **Read the TXT report** for a quick understanding
2. **Review the JSON** if you need structured data
3. **Watch the recording** to see the agent in action
4. **Use the test account** to manually verify findings

## Support

This tool is part of the yc-hackathon project. For issues:
1. Check the session recording URL to see what happened
2. Review the task output in the JSON file
3. Verify API keys are valid and have sufficient credits

---

**Happy Exploring! 🔍**

