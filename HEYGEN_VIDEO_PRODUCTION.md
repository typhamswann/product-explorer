# HeyGen Video Production - Complete Pipeline 🎬

## Overview

The complete video production pipeline that combines:
- HeyGen AI avatar narration
- Browser-Use live recordings
- Timeline-based synchronization

Creates professional demo videos with avatar presenter.

## Pipeline Architecture

```
Timeline + Course Data
    ↓
1. SCRIPT GENERATION (o3-mini)
   └─ Creates narration script with timestamps
    ↓
2. HEYGEN VIDEO GENERATION
   ├─ Intro: Full-screen avatar (12-15s)
   └─ Narration: Small avatar segments (5-15s each)
    ↓
3. VIDEO COMPOSITION (ffmpeg)
   ├─ Intro: Full screen avatar
   └─ Main: Browser recording + avatar overlay (top-right)
    ↓
Final Demo Video
```

## Components

### 1. Script Generator (`script_generator.py`)

**Purpose:** Generate narration script from timeline

**Input:**
- Timeline JSON (events, timing, agent reasoning)
- Course definition
- Product context

**Output:**
- Structured script with segments
- Intro + 5-8 narration points
- Timestamps aligned with timeline

**Example Script:**
```json
{
  "segments": [
    {
      "segment_id": 0,
      "segment_type": "intro",
      "start_time": 0,
      "duration": 12,
      "narration_text": "Welcome to this tutorial...",
      "context": "Introduction"
    },
    {
      "segment_id": 1,
      "segment_type": "narration",
      "start_time": 4.71,
      "duration": 5,
      "narration_text": "Now I'm logging in...",
      "context": "Login page"
    }
  ]
}
```

### 2. HeyGen Generator (`heygen_generator.py`)

**Purpose:** Create avatar videos for each script segment

**Input:**
- Script JSON with segments
- HeyGen API key

**Output:**
- Intro video (1280x720, full screen)
- Narration videos (320x180, for overlay)

**Process:**
1. Submit video generation to HeyGen API
2. Poll for completion (2-5 min per video)
3. Download MP4 files

### 3. Video Composer (`video_composer.py`)

**Purpose:** Combine everything into final video

**Input:**
- HeyGen intro video
- HeyGen narration segments
- Browser-Use live recording
- Script with timing

**Output:**
- Final composed MP4 with:
  - Full-screen intro
  - Browser recording with avatar overlay

## Video Structure

### Final Video Layout

**Part 1: Intro (0:00 - 0:12)**
```
┌────────────────────────────┐
│                            │
│     HeyGen Avatar          │
│     (Full Screen)          │
│                            │
│  "Welcome to this demo..." │
│                            │
└────────────────────────────┘
```

**Part 2: Demo (0:12 - end)**
```
┌────────────────────────────┐
│ ┌──────┐                   │
│ │Avatar│ Browser Recording │
│ │(PIP) │                   │
│ └──────┘                   │
│                            │
│  "Now I'm clicking..."     │
└────────────────────────────┘
```

## Usage

### Complete Pipeline

```bash
python explore.py https://www.spinstack.dev/ --execute-courses --generate-videos
```

This will:
1. Explore product
2. Generate courses
3. Execute & record
4. Generate scripts
5. Create HeyGen videos
6. Compose final videos

### Standalone

```bash
# Generate script
python script_generator.py

# Generate HeyGen videos
python heygen_generator.py

# Compose final video
python video_composer.py
```

## Technical Details

### Script Generation

**Model:** OpenAI o3-mini with structured outputs

**Prompt Strategy:**
- Analyze timeline events
- Extract key moments
- Generate concise narration
- Align with timestamps

**Output:** 6-10 segments per course

### HeyGen Video Generation

**API:** HeyGen v2/video/generate

**Settings:**
- Avatar: Professional presenter
- Voice: Natural TTS
- Background: White (intro) or Transparent (overlay)
- Dimensions: 1280x720 (intro) or 320x180 (PIP)

**Processing Time:** 2-5 minutes per segment

### Video Composition

**Tool:** ffmpeg with filter_complex

**Process:**
1. Intro: Play HeyGen video full screen
2. Main: Play browser recording
3. Overlay: Add HeyGen narration in top-right at timestamps
4. Output: Single MP4 file

## Example Output

### For Course 1

**Generated Files:**
```
course_1_SESSION_script.json          (Script)
heygen_segment_0_intro.mp4            (Intro video)
heygen_segment_1_narration.mp4        (Narration 1)
heygen_segment_2_narration.mp4        (Narration 2)
... (5-8 narration segments)
course_1_SESSION_live.webm            (Browser recording)
course_1_SESSION_final.mp4            (Composed video)
```

### Final Video Structure

```
0:00 - 0:12   Intro (avatar full screen)
0:12 - 0:17   Browser + avatar narration 1
0:17 - 0:23   Browser + avatar narration 2
0:23 - 0:28   Browser + avatar narration 3
... etc
```

## Benefits

### Professional Presentation
- ✅ Avatar presenter guides viewers
- ✅ Smooth narration
- ✅ Picture-in-picture during demo
- ✅ Polished final product

### Automated
- ✅ Script generated from timeline
- ✅ Videos created automatically
- ✅ Composition handled by ffmpeg
- ✅ No manual editing needed

### Scalable
- ✅ Works for any product
- ✅ Adapts to any course length
- ✅ Consistent quality
- ✅ Batch processing

## Cost

### Per Course Video

- Script generation: ~$0.01 (o3-mini)
- HeyGen intro: ~$0.10-0.20
- HeyGen narration: ~$0.05-0.10 per segment
- Composition: Free (local ffmpeg)

**Total:** ~$0.50-1.00 per course video

### For 5 Courses

**Total:** ~$2.50-5.00 for complete video package

## Requirements

- ffmpeg (for composition)
- HeyGen API key
- OpenAI API key (for scripts)
- Browser-Use live recordings

## Future Enhancements

- Add background music
- Synchronized lip-sync
- Multiple avatar styles
- Custom branding overlays
- Subtitle generation
- Multi-language support

---

**Creates professional demo videos with AI avatar narration! 🎬**

