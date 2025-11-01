# Course Execution - Automated Demo Recording 🎬

## Overview

The Course Executor automatically executes all generated educational demos in parallel, creating real browser recordings for each course.

## What It Does

After generating educational demos, the executor:
1. **Creates unique email accounts** for each course
2. **Executes courses in parallel** with staggered starts to avoid rate limits
3. **Handles email verification** automatically for each session
4. **Records full executions** with Browser-Use Cloud
5. **Saves all recording links** and credentials

## Complete Pipeline

```
Product URL
    ↓
1. Explore Product
    ├─ Sign up
    ├─ Verify email
    ├─ Explore thoroughly
    └─ Generate report
    ↓
2. Generate Educational Demos (o3-mini)
    ├─ Analyze exploration
    ├─ Create 5 progressive courses
    └─ Save as Markdown + JSON
    ↓
3. Execute All Courses (NEW!)
    ├─ Loop through each course
    ├─ Execute in parallel
    ├─ Handle verification
    └─ Record sessions
    ↓
Output: Exploration + Demos + Recordings
```

## Usage

### Full Pipeline (Recommended)
```bash
python explore.py https://www.spinstack.dev/ --execute-courses
```

This will:
1. Explore the product
2. Generate 5 educational demos
3. Execute all 5 demos in parallel
4. Create recordings for each

### Skip Course Execution
```bash
python explore.py https://www.spinstack.dev/
# Generates demos but doesn't execute them
```

### Standalone Course Execution
```bash
python course_executor.py [max_courses]

# Examples:
python course_executor.py     # Execute first 2 courses
python course_executor.py 5   # Execute all 5 courses
```

## How It Works

### Phase 1: Signup (Per Course)
- Creates unique email account
- Navigates to product
- Fills signup form
- Submits and waits for verification

### Phase 2: Verification (Per Course)
- Monitors email inbox
- Extracts verification link using GPT-4o
- Stops signup session
- Creates new session at verification URL

### Phase 3: Course Execution (Per Course)
- Navigates through verification
- Logs in if needed
- Executes step-by-step course instructions
- Records entire process

### Parallel Execution
- All courses execute simultaneously
- Staggered starts (10s intervals) to avoid rate limits
- Independent email accounts per course
- Separate sessions for each course

## Output

### Execution Report (Markdown)
```
course_executions_DOMAIN_TIMESTAMP_REPORT.md
```

Contains:
- Course titles
- Execution status
- Duration for each
- Email credentials
- Recording links

### Execution Data (JSON)
```
course_executions_DOMAIN_TIMESTAMP.json
```

Structured data with:
- All course execution details
- Session IDs
- Credentials
- Recording URLs
- Status and timing

## Example Output

```markdown
# Course Execution Report

## Execution Results

### Demo 1: Kickstart Your First Agent Flow

- **Status:** finished
- **Duration:** 56.8s
- **Email:** dullcamera685@agentmail.to
- **Password:** 4WL7m2w!6LfX8DhF
- **Recording:** https://cloud.browser-use.com/share/TAXvlofO05H7...

### Demo 2: Customizing Agent Flows

- **Status:** finished
- **Duration:** 130.8s
- **Email:** boredshirt333@agentmail.to
- **Password:** eef0f48i2x301C@W
- **Recording:** https://cloud.browser-use.com/share/wW4Xr5qsw8xT...
```

## Technical Details

### Parallel Execution Strategy
```python
# Create tasks for all courses
tasks = []
for i, course in enumerate(courses):
    email_client, inbox = await create_email()
    credentials = generate_credentials(inbox)
    
    task = execute_course(
        course, i, product_url,
        credentials, email_client, inbox
    )
    tasks.append(task)

# Execute all in parallel
results = await asyncio.gather(*tasks, return_exceptions=True)
```

### Rate Limit Handling
- Staggered starts: 10s * course_index
- Course 1: starts immediately
- Course 2: starts after 10s
- Course 3: starts after 20s
- Course 4: starts after 30s
- Course 5: starts after 40s

### Session Management
Each course uses TWO sessions:
1. **Signup Session**: Account creation only (discarded)
2. **Course Session**: Verification + demo execution (saved)

Only the course session recording is saved.

## Performance Metrics

### Execution Times (Spinstack Example)
- Course 1 (Beginner): ~57s
- Course 2 (Intermediate): ~131s
- Course 3 (Beginner): ~76s
- Course 4 (Advanced): ~151s
- Course 5 (Advanced): ~197s

### Resource Usage
- 2 sessions per course (signup + execution)
- 1 email account per course
- 2-3 tasks per course (signup, verify, execute)
- Total sessions for 5 courses: 10 sessions

### Success Rate
- Typical: 80-100% success rate
- Failed courses still produce recordings
- Rate limits: Managed with staggering

## Advanced Features

### Error Handling
- Exceptions caught and logged
- Failed courses don't stop others
- All results saved (success or fail)
- Detailed error messages in JSON

### Recording Quality
- Full browser sessions recorded
- Includes verification flow
- Shows actual UI interactions
- Shareable public links

### Credentials Management
- Unique email per course
- Secure random passwords
- All credentials saved
- Can be used for manual testing

## Use Cases

### Product Documentation
- Create video tutorials automatically
- Show exact UI workflows
- Generate onboarding content
- Build help center resources

### QA Testing
- Verify signup flows work
- Test email verification
- Validate course accuracy
- Check UI accessibility

### Sales Demos
- Create product showcases
- Build demo libraries
- Share with prospects
- Update automatically

### Training
- Create training materials
- Onboard new users
- Build certification courses
- Scale education

## Limitations

### Rate Limits
- Browser-Use Cloud has rate limits
- Staggering helps but doesn't eliminate
- May need to run in batches for many courses

### Execution Time
- Varies by course complexity
- 1-3 minutes per course typical
- Parallel execution reduces total time
- 5 courses: ~3-5 minutes total

### Verification Dependency
- Requires email verification to work
- Products without verification may fail
- Manual intervention needed for CAPTCHAs
- Some signup flows incompatible

## Troubleshooting

### "No verification email received"
- Check AgentMail inbox
- Verify email sending works
- Increase timeout
- Check spam filters

### "Rate limit hit"
- Increase stagger delay
- Run fewer courses at once
- Wait between executions
- Use different API key

### "Session stopped early"
- Check recording to see why
- May be CAPTCHA or bot detection
- Product may have restrictions
- Try manual execution

## File Structure

```
explore_product/
├── course_executor.py          # Course execution logic
├── explore.py                   # Integrated pipeline
└── outputs/
    ├── course_executions_*.json
    ├── course_executions_*_REPORT.md
    ├── demos_*.json
    ├── demos_*_COURSES.md
    ├── exploration_*.json
    └── exploration_*_REPORT.txt
```

## API Cost

### Per 5-Course Execution
- Email creation: Free (AgentMail)
- Browser sessions: ~10 sessions
- GPT-4o calls: ~5 for verification extraction
- Total cost: ~$0.05-0.10 per full execution

## Future Enhancements

### Potential Improvements
1. **Screenshot capture** at each step
2. **Video editing** to create polished tutorials
3. **Voiceover generation** using TTS
4. **Subtitle addition** for accessibility
5. **Multi-language support** for demos
6. **Custom branding** overlays
7. **Analytics tracking** on recordings
8. **Interactive elements** in recordings

---

**The Course Executor brings your educational demos to life with real, working recordings! 🎬**

