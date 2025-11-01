# Live Video Recording - Actual Browser Execution Videos 🎥

## Overview

Records the **actual live browser session** as it executes, capturing real-time interactions as downloadable WebM video files.

## How It Works

### The Approach

1. **Browser-Use** creates a session with a `liveUrl`
2. **Playwright** opens that `liveUrl` in a browser
3. **Playwright** records the browser tab as video
4. **Monitor** the task until completion
5. **Save** the video file when done

### Technical Implementation

```
Course Execution Starts
    ↓
Get liveUrl from session
    ↓
Playwright opens liveUrl in browser
    ├─ Enable video recording
    └─ Record browser tab
    ↓
Monitor task status (poll every 5s)
    ↓
Task finishes
    ↓
Stop recording
Close browser
    ↓
Save video as WebM file
```

### Code Flow

```python
# Open live URL in Playwright browser with recording
async with async_playwright() as p:
    browser = await p.chromium.launch(headless=False)
    
    context = await browser.new_context(
        record_video_dir="./outputs",
        record_video_size={"width": 1280, "height": 720}
    )
    
    page = await context.new_page()
    await page.goto(live_url)  # Open the live stream
    
    # Monitor task until complete
    await monitor_task_completion(task_id)
    
    # Get video and close
    video_path = await page.video.path()
    await page.close()
    await context.close()
    
    # Video is now saved!
```

## What You Get

### Per Course Execution

**4 Output Files:**
1. **Timeline JSON** - Events with timestamps
2. **Enhanced Script** - With agent reasoning
3. **Clean MDX** - Production-ready docs
4. **Live Video (WebM)** - Actual browser recording! 🆕

### Video Specifications

- **Format:** WebM (VP8/VP9 codec)
- **Resolution:** 1280x720 (720p)
- **Frame Rate:** Variable (Playwright default)
- **Size:** 1-3 MB per minute typical
- **Playable in:** All modern browsers, VLC, etc.

## Usage

### Automatic (Integrated)

Live video recording happens automatically during course execution:

```bash
python explore.py https://www.spinstack.dev/ --execute-courses
```

**Output:** Each course gets a `course_N_SESSION_live.webm` file

### Standalone Test

```bash
python live_video_recorder.py
```

Tests the video recorder with a short session.

## Real Example

### Course 1 Output

**Files Generated:**
```
course_0_456e723a_timeline.json          (12 KB)
course_0_456e723a_SCRIPT.md              (9 KB)
course_1_navigating-spinstack.mdx        (5 KB)
course_1_456e723a_live.webm              (1.7 MB) ← VIDEO!
```

**Video Details:**
- Duration: ~55 seconds
- Size: 1.7 MB
- Format: WebM
- Resolution: 1280x720

**Playback:**
```bash
open course_1_456e723a_live.webm
# Or drag into browser
```

## Video Content

The video shows:
- ✅ Actual live browser window
- ✅ Real-time UI interactions
- ✅ Page navigations
- ✅ Form submissions
- ✅ Button clicks
- ✅ Everything the agent does

**It's the REAL execution, not a screenshot slideshow!**

## Parallel Recording

### How It Works

Each course gets its own Playwright browser instance:

```
Course 1 → Playwright Browser 1 → Recording 1
Course 2 → Playwright Browser 2 → Recording 2
Course 3 → Playwright Browser 3 → Recording 3
```

All record simultaneously and independently.

### Resource Usage

- **CPU:** Moderate (one browser per course)
- **Memory:** ~500 MB per browser
- **Disk:** ~1-3 MB per minute per video

For 5 courses:
- ~2.5 GB RAM needed
- ~25-50 MB total video size

## Integration with Pipeline

### Complete Output Per Course

```
Course 1 Execution:
├─ Timeline JSON          (Raw data with agent reasoning)
├─ Enhanced SCRIPT.md     (Human-readable with reasoning)
├─ Clean MDX             (Production docs)
├─ Live VIDEO.webm       (Actual browser recording!) 🆕
├─ Share URL             (Interactive web replay)
└─ Credentials           (For manual testing)
```

### Report Includes Video

Execution report shows:
```markdown
### Demo 1: Navigating SpinStack

- **Status:** finished
- **Duration:** 54.8s
- **Share URL:** https://cloud.browser-use.com/share/...
- **Live Video:** `course_1_SESSION_live.webm` ← NEW!
- **Timeline:** `course_0_SESSION_timeline.json`
```

## Advantages Over Public Share

### Public Share URL
- ✅ Shareable link
- ✅ No download needed
- ❌ Requires internet
- ❌ Browser-Use platform dependent
- ❌ Screenshot-based replay

### Live Video (WebM)
- ✅ Downloadable file
- ✅ Works offline
- ✅ Platform independent
- ✅ ACTUAL smooth video
- ✅ Can edit/process
- ✅ Upload to YouTube, Vimeo, etc.

## Use Cases

### 1. Documentation Sites
Embed videos directly:
```html
<video controls>
  <source src="course_1_live.webm" type="video/webm">
</video>
```

### 2. Video Platforms
Upload to:
- YouTube
- Vimeo
- Wistia
- Loom

### 3. LMS Platforms
- Teachable
- Thinkific
- Custom platforms

### 4. Local Playback
- Download and watch
- Share via Dropbox/Drive
- Present offline

### 5. Video Editing
- Import into editing software
- Add voiceovers
- Create compilations
- Add branding

## Technical Details

### Playwright Video Recording

```python
# Context with video recording enabled
context = await browser.new_context(
    record_video_dir="./outputs",
    record_video_size={"width": 1280, "height": 720}
)

# Page automatically records
page = await context.new_page()

# When page closes, video is saved
await page.close()
video_path = await page.video.path()
```

### Task Monitoring

Key fix: Monitor **task status**, not session status

```python
# Sessions stay active after tasks finish!
# Must monitor task:

task_response = requests.get(f"/tasks/{task_id}")
task_status = task_response.json()['status']

if task_status in ['finished', 'stopped', 'failed']:
    # Stop recording
    await page.close()
```

### Video Format

- **Codec:** VP8 or VP9 (WebM)
- **Container:** WebM
- **Audio:** None (browser session has no audio)
- **Compatibility:** All modern browsers + VLC

### Converting to MP4 (Optional)

```bash
# Convert WebM to MP4 using ffmpeg
ffmpeg -i course_1_live.webm -c:v libx264 course_1_live.mp4
```

## Performance

### Recording Overhead

- **CPU:** Minimal (Playwright handles efficiently)
- **Memory:** ~500 MB per browser instance
- **Disk:** ~1-3 MB per minute

### Timing

- **Setup:** ~5 seconds (launch browser, load live URL)
- **Recording:** Duration of task
- **Cleanup:** ~3 seconds (close browser, save video)

### Total Time Per Course

- Without video: ~60s
- With video: ~60s (parallel recording!)

**No performance impact** - recording runs in parallel with execution.

## Troubleshooting

### Browser doesn't open
- Check Playwright is installed: `python3 -m playwright install chromium`
- Verify headless=False in launch options

### Video file not created
- Check Playwright video path exists
- Verify page.video.path() returns valid path
- Ensure page closed properly

### Video file is empty
- Task might have failed immediately
- Check estimated_duration is sufficient
- Verify live URL is valid

### Multiple browsers open
- Normal! Each course opens its own browser
- They close automatically when recording ends

## Benefits

### For Users
- ✅ Downloadable videos
- ✅ Offline playback
- ✅ Share anywhere
- ✅ Edit and customize

### For Creators
- ✅ Upload to platforms
- ✅ Embed in docs
- ✅ Create compilations
- ✅ Add voiceovers

### For Teams
- ✅ Internal sharing (no external dependency)
- ✅ Archive recordings
- ✅ Present offline
- ✅ Full control

## Complete Output Package

For each course, you now get:

```
Course 1:
├─ course_0_SESSION_timeline.json       (12 KB - data)
├─ course_0_SESSION_SCRIPT.md           (9 KB - narrative)
├─ course_1_navigating-spinstack.mdx    (5 KB - docs)
├─ course_1_SESSION_live.webm           (1.7 MB - VIDEO!) 🆕
├─ Share URL                             (Web replay)
└─ Credentials                           (Testing)
```

**Total:** 6 artifacts per course!

## Future Enhancements

### Potential Improvements
1. **Audio narration** - Add voiceover from agent reasoning
2. **Higher resolution** - 1080p or 4K
3. **Variable quality** - Adjust bitrate
4. **MP4 output** - Convert automatically
5. **Thumbnails** - Extract first frame
6. **Chapters** - Add from timeline
7. **Subtitles** - Generate from agent reasoning

---

**You now have ACTUAL video files of the live browser execution! 🎥🎬**

