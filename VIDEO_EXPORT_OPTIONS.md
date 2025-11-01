# Video Export Options - Getting Actual Video Demos 🎥

## Current Situation

Browser-Use Cloud provides two types of session URLs:

### 1. Live URL (During Execution)
```
https://live.browser-use.com?wss=https://SESSION.cdp0.browser-use.com
```

**What it is:** Real-time WebSocket connection to running browser  
**Shows:** Actual browser executing live  
**Available:** Only during execution  
**Format:** Interactive stream (not downloadable)

### 2. Public Share URL (After Execution)
```
https://cloud.browser-use.com/share/SHARE_TOKEN
```

**What it is:** Interactive replay of the session  
**Shows:** Step-by-step playback with screenshots  
**Available:** Permanently after session ends  
**Format:** Web-based player (not downloadable video)

## The Problem

Neither URL provides a downloadable video file (MP4, WebM, etc.). They are:
- Live URL: Real-time stream (gone after execution)
- Public Share: Interactive web player (not a video file)

## Solutions

### Option 1: Screen Record During Live Execution ⭐ RECOMMENDED

**Approach:** Record the `liveUrl` while the task executes

**How:**
1. Start browser automation
2. Open `liveUrl` in a browser
3. Use screen recording tool to capture the browser window
4. Save as MP4/WebM

**Tools:**
- **macOS:** Built-in screen recording (`Cmd+Shift+5`)
- **ffmpeg:** `ffmpeg -f avfoundation -i "1" output.mp4`
- **Python:** `pyautogui` + `opencv-python` for programmatic recording
- **OBS Studio:** Professional screen recording

**Pros:**
- ✅ Gets real browser execution
- ✅ Captures actual UI interactions
- ✅ No post-processing needed
- ✅ Full video quality

**Cons:**
- ❌ Requires recording during execution
- ❌ Needs screen recording tool
- ❌ Manual intervention or automation
- ❌ Can't record parallel sessions easily

**Implementation:**
```python
import subprocess
import time

# Start recording
def record_live_session(live_url, duration, output_file):
    # Open live URL in browser
    subprocess.Popen(['open', live_url])
    
    # Wait for browser to load
    time.sleep(3)
    
    # Start screen recording (macOS example)
    # This is pseudo-code - actual implementation would use
    # screen recording libraries or external tools
    
    # Wait for duration
    time.sleep(duration)
    
    # Stop recording
```

### Option 2: Record the Public Share Replay

**Approach:** Play the public share URL and record it

**How:**
1. Course finishes execution
2. Get `publicShareUrl`
3. Open URL in browser
4. Click play on the replay
5. Screen record the playback

**Tools:** Same as Option 1

**Pros:**
- ✅ Can be done after execution
- ✅ Replay is permanent
- ✅ Can record at any time

**Cons:**
- ❌ Still requires screen recording
- ❌ Replay might be screenshot-based (less smooth)
- ❌ Not true video capture

### Option 3: Create Video from Screenshots + Timeline 🤖

**Approach:** Use captured screenshots and timeline to generate video

**How:**
1. Download all screenshots from timeline
2. Use timeline timestamps as frame durations
3. Combine into video using ffmpeg
4. Add annotations/overlays

**Tools:**
- `ffmpeg` - Video creation from images
- `PIL/Pillow` - Image processing
- Timeline JSON - Timing data

**Implementation:**
```python
import requests
from PIL import Image
import subprocess

def create_video_from_timeline(timeline_data, output_file):
    events = timeline_data['events']
    
    # Download screenshots
    images = []
    for event in events:
        screenshot_url = event.get('screenshot_url')
        if screenshot_url:
            # Download image
            response = requests.get(screenshot_url)
            image_path = f"frame_{event['step_number']}.png"
            with open(image_path, 'wb') as f:
                f.write(response.content)
            images.append(image_path)
    
    # Create video with ffmpeg
    # Calculate duration per frame from timeline
    durations = []
    for i in range(len(events) - 1):
        duration = events[i+1]['t_offset_s'] - events[i]['t_offset_s']
        durations.append(duration)
    
    # Use ffmpeg to create video
    # (Complex ffmpeg command needed to set per-frame duration)
```

**Pros:**
- ✅ Automated - no manual recording
- ✅ Works with timeline data
- ✅ Can add annotations
- ✅ Parallel-friendly

**Cons:**
- ❌ Screenshot-based (not smooth video)
- ❌ Requires ffmpeg
- ❌ Missing transitions between screenshots
- ❌ More like slideshow than video

### Option 4: Use Browser DevTools Protocol Recording

**Approach:** Capture browser session using CDP (Chrome DevTools Protocol)

**How:**
Browser-Use Cloud uses CDP internally. Theoretically:
1. Access CDP events during session
2. Capture screencast frames
3. Combine into video

**Reality:**
- Browser-Use Cloud API doesn't expose CDP recording capabilities
- Would need to run browser locally (not cloud)
- Complex implementation

**Verdict:** Not feasible with Browser-Use Cloud

### Option 5: Automated Screen Recording During Execution ⭐ BEST FOR YOUR USE CASE

**Approach:** Programmatically record the live browser during execution

**Implementation Strategy:**

```python
# In course_executor.py, add automated recording

import subprocess
import threading

class LiveRecorder:
    def __init__(self, live_url, duration):
        self.live_url = live_url
        self.duration = duration
        self.process = None
    
    def start_recording(self, output_file):
        # Open live URL in browser
        subprocess.Popen([
            'open', '-a', 'Google Chrome',
            '--args', '--new-window', self.live_url
        ])
        
        # Wait for browser to load
        time.sleep(5)
        
        # Start ffmpeg screen recording (macOS)
        # Capture specific window or screen region
        self.process = subprocess.Popen([
            'ffmpeg',
            '-f', 'avfoundation',
            '-i', '1',  # Display capture
            '-t', str(self.duration),
            '-vcodec', 'libx264',
            '-preset', 'ultrafast',
            output_file
        ])
    
    def stop_recording(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
```

**Usage:**
```python
# When executing course
recorder = LiveRecorder(live_url, estimated_duration=120)
recorder.start_recording(f'course_{index}_video.mp4')

# Execute course...
await execute_course()

recorder.stop_recording()
```

**Pros:**
- ✅ Automated recording
- ✅ Real browser execution
- ✅ Actual video file (MP4)
- ✅ Can run during parallel execution (if recording separate displays)

**Cons:**
- ❌ Requires ffmpeg installed
- ❌ macOS/Linux specific commands
- ❌ May need window management
- ❌ Parallel recording requires multiple displays or virtual displays

### Option 6: Puppeteer Recorder (If Running Locally)

**Approach:** Use Puppeteer's built-in recording

**Note:** This would require running Browser-Use locally, not via Cloud API

**Not applicable** for your current Cloud-based setup

## Recommended Approach for Your Setup

### Two-Tier Strategy:

#### Tier 1: Keep Public Share URLs (What You Have Now)
**Purpose:** Interactive replays for immediate sharing

**Current Implementation:** ✅ Working
- Each course has a public share URL
- Shareable immediately
- No download needed
- Works on any device

**Use For:**
- Quick sharing with stakeholders
- Internal review
- Documentation links
- Browser-based viewing

#### Tier 2: Add Automated Live Recording (New)
**Purpose:** Downloadable MP4 videos

**Implementation Options:**

**A. Simple Approach - Record One Session at a Time:**
```python
# Modify course_executor to record the first course only
# (for demo purposes)

if course_index == 0:
    # Open live URL in browser
    subprocess.Popen(['open', live_url])
    
    # Use macOS screen recording or ffmpeg
    # Record the browser window
    # Save as MP4
```

**B. Advanced Approach - Headless Browser Recording:**
```python
# Use Playwright or Selenium locally to:
# 1. Open the live URL
# 2. Start video capture
# 3. Record the browser viewport
# 4. Save as video file
```

**C. Post-Processing Approach:**
```python
# Use screenshots from timeline:
# 1. Download all screenshots
# 2. Create video slideshow with ffmpeg
# 3. Add timing from timeline
# 4. Export as MP4
```

## What Browser-Use Cloud Actually Provides

Based on the API and documentation:

### Public Share URL Format
```
https://cloud.browser-use.com/share/TOKEN
```

**Opens to:** Web-based replay player

**Player Features:**
- Step-by-step playback
- Screenshots from execution
- Can see what happened
- Interactive timeline

**IS IT A VIDEO?** No - it's an interactive player with screenshots

**CAN YOU DOWNLOAD IT?** Not directly - it's web-based

## Practical Solutions

### For Your Use Case:

#### What You Need:
- Downloadable video files per course
- Automated (minimal manual intervention)
- Works with parallel execution

#### Best Solution: Screenshot-to-Video Conversion

**Why:** You already have:
- ✅ Screenshots at every step (timeline)
- ✅ Precise timestamps
- ✅ Works with all courses
- ✅ Fully automated

**Implementation:**
```python
def create_video_from_timeline(timeline_file, output_video):
    import requests
    from pathlib import Path
    import subprocess
    
    # Load timeline
    with open(timeline_file) as f:
        timeline = json.load(f)
    
    # Download screenshots
    screenshot_dir = Path(f"screenshots_{timeline['session_id']}")
    screenshot_dir.mkdir(exist_ok=True)
    
    frame_list = []
    
    for i, event in enumerate(timeline['events']):
        screenshot_url = event.get('screenshot_url')
        if screenshot_url:
            # Download
            response = requests.get(screenshot_url)
            frame_path = screenshot_dir / f"frame_{i:03d}.png"
            with open(frame_path, 'wb') as f:
                f.write(response.content)
            
            # Calculate duration (how long to show this frame)
            if i < len(timeline['events']) - 1:
                duration = timeline['events'][i+1]['t_offset_s'] - event['t_offset_s']
            else:
                duration = 2.0  # Last frame
            
            frame_list.append((frame_path, duration))
    
    # Create video with ffmpeg
    # Build complex filter for variable frame durations
    create_video_with_variable_durations(frame_list, output_video)
```

#### Alternative: Use OBS + Live URL During Execution

**Setup:**
1. Install OBS Studio
2. Configure browser source pointing to live URL
3. Start OBS recording before course execution
4. Stop after completion

**Automated with:**
```python
# obswebsocket library for OBS automation
from obswebsocket import obsws, requests as obs_requests

obs = obsws("localhost", 4444, "password")
obs.connect()

# Start recording
obs.call(obs_requests.StartRecording())

# Execute course...

# Stop recording
obs.call(obs_requests.StopRecording())
```

## Recommendation

Given your requirements and setup, I recommend:

### Immediate Solution (Works Now)
**Use the public share URLs you already have**
- They're shareable immediately
- Work on any device
- No additional implementation needed
- Good enough for most use cases

### For Actual Video Files
**Implement screenshot-to-video conversion**
- Fully automated
- Works with existing timeline data
- Can process all courses in parallel
- Generates MP4 files

**I can implement this if you'd like!**

## Implementation Plan for Video Export

If you want downloadable videos, here's what I'd add:

```python
# video_generator.py

class VideoGenerator:
    def create_video_from_timeline(self, timeline_file):
        # 1. Load timeline JSON
        # 2. Download all screenshots
        # 3. Use timeline timestamps for frame durations
        # 4. Create video with ffmpeg:
        #    - Concat screenshots as frames
        #    - Set duration per frame from timeline
        #    - Add optional overlays (step numbers, timestamps)
        # 5. Output: course_N_video.mp4
```

Would you like me to implement the screenshot-to-video converter?

---

**Summary:** Browser-Use provides interactive replays (web player), not downloadable videos. For MP4 files, you need either screen recording during execution or converting screenshots to video using timeline data.

