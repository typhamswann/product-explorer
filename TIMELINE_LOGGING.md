# Timeline Logging - Event Tracking with Timestamps 📊

## Overview

Every course execution now captures a detailed timeline of events with timestamps and URLs, creating a perfect mapping between the browser recording and what happened at each moment.

## What Gets Captured

### Per Course Timeline

Each executed course generates:
1. **Timeline JSON** - Structured event log with timestamps
2. **Annotated Report** - Human-readable timeline preview
3. **Recording URL** - Browser session replay
4. **Credentials** - Email + password for manual testing

### Event Data Structure

```json
{
  "step_number": 1,
  "t_offset_s": 4.68,
  "t_formatted": "00:04",
  "url": "https://www.spinstack.dev/agent-studio",
  "action": "",
  "extracted_content": "",
  "timestamp": "2025-11-01T09:20:01.232156"
}
```

**Fields:**
- `step_number` - Sequential step number (1, 2, 3...)
- `t_offset_s` - Time offset from task start in seconds
- `t_formatted` - Human-readable time (MM:SS)
- `url` - Current page URL at this step
- `action` - Action taken (from Browser-Use API)
- `extracted_content` - Content extracted (if any)
- `timestamp` - Absolute ISO timestamp

## Output Files

### Per-Course Timeline JSON
```
course_{index}_{session_id}_timeline.json
```

Example: `course_0_9501a6a6-a73e-4416-89d5-ac34d5f81c01_timeline.json`

**Contains:**
```json
{
  "course_index": 0,
  "course_title": "Demo 1: Kickstart Your First Agent Flow",
  "session_id": "9501a6a6-a73e-4416-89d5-ac34d5f81c01",
  "task_id": "eb78915b-23e4-4d89-9c22-3e5af7af6bed",
  "recording_url": "https://cloud.browser-use.com/share/...",
  "duration_seconds": 59.73,
  "total_steps": 9,
  "events": [...]
}
```

### Execution Report (with Timeline Preview)
```
course_executions_{domain}_{timestamp}_REPORT.md
```

**Includes Timeline Table:**
```markdown
**Timeline Preview:**

| Time | Step | URL |
|------|------|-----|
| 00:04 | 1 | https://www.spinstack.dev/auth/login... |
| 00:09 | 2 | https://www.spinstack.dev/agent-studio |
| 00:11 | 3 | https://www.spinstack.dev/products |
| 00:16 | 5 | https://www.spinstack.dev/agent-studio |
```

## How It Works

### Timeline Capture Process

1. **Task Started** - Record start time
2. **Poll Every 2 Seconds** - Check for new steps
3. **Capture Events** - Log each new step with:
   - Time offset from start
   - Current URL
   - Step number
   - Timestamp
4. **Task Completed** - Save timeline to file

### Technical Implementation

```python
# Start capture
start_time = time.time()
timeline_events = []

# Poll for steps
while task_running:
    task_data = get_task_status(task_id)
    steps = task_data.get('steps', [])
    
    # Log new steps
    for step in new_steps:
        event = {
            'step_number': i + 1,
            't_offset_s': time.time() - start_time,
            't_formatted': format_mm_ss(offset),
            'url': step['url'],
            'timestamp': datetime.now().isoformat()
        }
        timeline_events.append(event)

# Save timeline
save_timeline(timeline_events, session_id)
```

### Parallel Execution

Timeline capture works independently for each course:
- Course 1: Own timeline file
- Course 2: Own timeline file
- Course 3: Own timeline file
- All execute in parallel
- No interference between timelines

## Usage

### Automatic Capture (Default)

Timeline capture is enabled by default:

```bash
# Full pipeline with timeline
python explore.py https://www.spinstack.dev/ --execute-courses

# Standalone execution with timeline
python course_executor.py 2
```

### Disable Timeline Capture

```python
# In code
executor.execute_course(
    course, index, url, credentials,
    email_client, inbox,
    capture_timeline=False  # Disable
)
```

## Timeline Use Cases

### 1. Navigate Recordings

**Problem**: Hard to find specific moments in recording  
**Solution**: Use timeline to jump to exact timestamps

```
Recording at 00:16 → Shows "Navigate to Products page"
Recording at 00:27 → Shows "Create new agent flow"
```

### 2. Verify Course Accuracy

**Problem**: Did the agent follow the course steps?  
**Solution**: Compare timeline URLs to expected course flow

```
Expected: Home → Products → Agent Studio
Timeline: ✅ Matches expected flow
```

### 3. Debug Failures

**Problem**: Course failed, don't know where  
**Solution**: Check last timeline event

```
Last event: t=00:45, url=/error  
Issue: Failed at step 12 (error page)
```

### 4. Create Annotated Tutorials

**Problem**: Need to reference specific moments  
**Solution**: Use timeline to add [t=MM:SS] markers

```markdown
1. Click Create [t=00:11]
2. Enter product name [t=00:16]
3. Submit form [t=00:22]
```

### 5. Measure Performance

**Problem**: Which steps take longest?  
**Solution**: Calculate deltas between events

```
Step 1→2: 5s (fast)
Step 2→3: 2s (fast)
Step 3→4: 15s (slow - investigate)
```

## Example Output

### Test Results (Spinstack)

**Course 1: Kickstart Your First Agent Flow**
- Duration: 59.7s
- Events Captured: 9 steps
- Recording: https://cloud.browser-use.com/share/w3-OU0Ut37mvNW4S7GgkwA_5Hta9d-ni
- Timeline: `course_0_..._timeline.json`

**Timeline Events:**
```
[00:04] Step 1: /auth/login
[00:09] Step 2: /auth/login
[00:11] Step 3: /agent-studio
[00:13] Step 4: /agent-studio
[00:16] Step 5: /products
[00:18] Step 6: /agent-studio
[00:20] Step 7: /agent-studio
[00:22] Step 8: /agent-studio
[00:27] Step 9: /agent-studio
```

**Course 2: Customizing Agent Flows**
- Duration: 118.4s
- Events Captured: 30 steps
- Recording: https://cloud.browser-use.com/share/dTiLF3hCfA4JjW36UQLdQy8SdwXGVtrV
- Timeline: `course_1_..._timeline.json`

## Timeline Data Analysis

### Load Timeline

```python
import json

with open('course_0_..._timeline.json') as f:
    timeline = json.load(f)

# Access events
for event in timeline['events']:
    print(f"[{event['t_formatted']}] {event['url']}")
```

### Calculate Step Durations

```python
events = timeline['events']

for i in range(len(events) - 1):
    current = events[i]
    next_event = events[i + 1]
    duration = next_event['t_offset_s'] - current['t_offset_s']
    print(f"Step {current['step_number']}: {duration:.1f}s")
```

### Find URL Changes

```python
url_changes = []

for i, event in enumerate(events):
    if i == 0 or event['url'] != events[i-1]['url']:
        url_changes.append({
            'time': event['t_formatted'],
            'from': events[i-1]['url'] if i > 0 else 'start',
            'to': event['url']
        })

print(f"URL changed {len(url_changes)} times")
```

## Integration with Recordings

### Timeline + Recording = Perfect Documentation

**Without Timeline:**
- Recording shows actions
- Hard to reference specific moments
- Manual scrubbing to find events

**With Timeline:**
- Recording shows actions
- Timeline provides exact timestamps
- Direct reference to any moment
- Can annotate scripts with times

### Example Annotated Script

```markdown
# Course: Create Your First Agent Flow

**Recording:** https://cloud.browser-use.com/share/...
**Timeline:** course_0_..._timeline.json

## Steps

1. **[00:04] Login to Spinstack**
   - URL: /auth/login
   - Enter credentials and submit

2. **[00:11] Navigate to Agent Studio**
   - URL: /agent-studio
   - Click "Agent Studio" in navigation

3. **[00:16] Go to Products Page**
   - URL: /products
   - Click "Products" in sidebar

4. **[00:18] Return to Agent Studio**
   - URL: /agent-studio
   - Click "Create New Product"
```

## Advanced Features

### Timeline Filtering

```python
# Get only URL changes
url_changes = [
    e for i, e in enumerate(events)
    if i == 0 or e['url'] != events[i-1]['url']
]

# Get steps within time range
minute_1_steps = [
    e for e in events
    if 0 <= e['t_offset_s'] < 60
]

# Get steps on specific page
agent_studio_steps = [
    e for e in events
    if '/agent-studio' in e['url']
]
```

### Timeline Visualization

```python
# Create simple text visualization
for event in events:
    bar_length = int(event['t_offset_s'] / 2)
    bar = '█' * bar_length
    print(f"{event['t_formatted']} {bar} {event['url'][-30:]}")
```

### Export for Video Editing

```python
# Convert to video chapter markers
for event in events:
    mins = int(event['t_offset_s'] // 60)
    secs = int(event['t_offset_s'] % 60)
    print(f"{mins:02d}:{secs:02d} - Step {event['step_number']}")
```

## Limitations

### What Timeline Doesn't Capture

1. **Visual Changes** - Only URLs, not UI state
2. **Sub-second Events** - Polls every 2 seconds
3. **Failed Actions** - Only successful steps logged
4. **User Input** - No form data captured
5. **JavaScript Events** - Only page navigations

### What Timeline Does Capture

1. ✅ **Page URLs** - Every navigation
2. ✅ **Step Sequence** - Order of operations
3. ✅ **Timing** - When each step occurred
4. ✅ **Duration** - Total execution time
5. ✅ **Session Mapping** - Links to recording

## Best Practices

### For Analysis
- Use timeline to understand flow
- Calculate step durations
- Identify bottlenecks
- Compare courses

### For Documentation
- Add [t=MM:SS] markers to tutorials
- Reference timeline in guides
- Link to recording moments
- Create chapter markers

### For Debugging
- Check last successful step
- Find where it diverged
- Measure step times
- Identify slow steps

### For Testing
- Verify expected URLs visited
- Confirm step sequence
- Check timing constraints
- Validate course accuracy

## Future Enhancements

### Potential Improvements

1. **Screenshot Capture** - Save image at each step
2. **Action Descriptions** - Capture what was clicked
3. **Form Data** - Log input values (sanitized)
4. **Error Events** - Capture failures
5. **Video Chapters** - Auto-generate for recordings
6. **Timeline Diff** - Compare expected vs actual
7. **Performance Metrics** - Speed analysis
8. **Timeline Replay** - Visualize execution

---

**Timeline logging creates a perfect bridge between browser recordings and structured course data! 📊🎥**

