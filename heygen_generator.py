"""
HeyGen Video Generator - Create avatar narration videos
Uses HeyGen API to generate avatar videos for script segments
"""

import asyncio
import json
import os
import time
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()


class HeyGenGenerator:
    """Generate avatar videos using HeyGen API"""
    
    def __init__(self, api_key: str, output_dir: str = "./outputs"):
        self.api_key = api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.base_url = "https://api.heygen.com"
        
        # Avatar and voice
        # Using user's custom "Agent" avatar group
        self.avatar_id = "ade9d90c5cd64482abbd5aaf15069c4a"  # Agent avatar group
        self.voice_id = "Xfk8GMWcOK3klRS7h9s3"  # Agent's default voice
    
    async def generate_segment_video(
        self,
        segment: Dict[str, Any],
        segment_index: int
    ) -> Optional[str]:
        """Generate a single HeyGen video for a script segment."""
        
        narration_text = segment.get('narration_text', '')
        segment_type = segment.get('segment_type', 'narration')
        
        print(f"   🎬 Generating HeyGen video for segment {segment_index}")
        print(f"      Type: {segment_type}")
        print(f"      Text: {narration_text[:60]}...")
        
        # Create video request
        payload = {
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": self.avatar_id,
                        "avatar_style": "normal"
                    },
                    "voice": {
                        "type": "text",
                        "input_text": narration_text,
                        "voice_id": self.voice_id
                    },
                    "background": {
                        "type": "color",
                        "value": "#FFFFFF"  # White background for all segments
                    }
                }
            ],
            "dimension": {
                "width": 1280 if segment_type == "intro" else 320,  # Smaller for overlay
                "height": 720 if segment_type == "intro" else 180
            },
            "test": False  # Set to False for production (removes watermark)
        }
        
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            # Submit video generation
            response = requests.post(
                f"{self.base_url}/v2/video/generate",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            video_id = result.get('data', {}).get('video_id')
            if not video_id:
                print(f"      ❌ No video_id in response")
                return None
            
            print(f"      ✅ Video ID: {video_id}")
            
            # Wait for video to be ready
            video_url = await self._wait_for_video(video_id, headers)
            
            if not video_url:
                return None
            
            # Download the video
            video_file = await self._download_video(
                video_url,
                segment_index,
                segment_type
            )
            
            return video_file
            
        except Exception as e:
            print(f"      ❌ HeyGen API error: {e}")
            return None
    
    async def _wait_for_video(
        self,
        video_id: str,
        headers: Dict[str, str],
        max_wait: int = 300
    ) -> Optional[str]:
        """Wait for HeyGen video to be ready."""
        
        print(f"      ⏳ Waiting for video to be ready...")
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            await asyncio.sleep(5)
            
            try:
                response = requests.get(
                    f"{self.base_url}/v1/video_status.get?video_id={video_id}",
                    headers=headers
                )
                response.raise_for_status()
                status_data = response.json()
                
                status = status_data.get('data', {}).get('status')
                elapsed = time.time() - start_time
                
                print(f"         [{elapsed:.0f}s] Status: {status}")
                
                if status == 'completed':
                    video_url = status_data.get('data', {}).get('video_url')
                    print(f"      ✅ Video ready!")
                    return video_url
                
                elif status == 'failed':
                    error = status_data.get('data', {}).get('error')
                    print(f"      ❌ Video generation failed: {error}")
                    return None
                    
            except Exception as e:
                print(f"         ⚠️  Status check error: {e}")
                await asyncio.sleep(5)
        
        print(f"      ❌ Timeout waiting for video")
        return None
    
    async def _download_video(
        self,
        video_url: str,
        segment_index: int,
        segment_type: str
    ) -> str:
        """Download HeyGen video."""
        
        filename = f"heygen_segment_{segment_index}_{segment_type}.mp4"
        filepath = self.output_dir / filename
        
        print(f"      📥 Downloading video...")
        
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size_mb = filepath.stat().st_size / 1024 / 1024
        print(f"      ✅ Downloaded: {filename} ({file_size_mb:.1f} MB)")
        
        return str(filepath)
    
    async def generate_all_segments(
        self,
        script: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate HeyGen videos for all script segments."""
        
        segments = script.get('segments', [])
        
        print(f"\n{'='*80}")
        print(f"🎬 HEYGEN VIDEO GENERATION")
        print(f"{'='*80}")
        print(f"Course: {script.get('course_title')}")
        print(f"Segments: {len(segments)}")
        print(f"{'='*80}\n")
        
        results = []
        
        # Generate intro first
        intro_segments = [s for s in segments if s.get('segment_type') == 'intro']
        if intro_segments:
            intro = intro_segments[0]
            video_file = await self.generate_segment_video(intro, 0)
            results.append({
                'segment_id': intro.get('segment_id', 0),
                'type': 'intro',
                'video_file': video_file,
                'text': intro.get('narration_text')
            })
        
        # Generate narration segments
        narration_segments = [s for s in segments if s.get('segment_type') == 'narration']
        for i, segment in enumerate(narration_segments, 1):
            video_file = await self.generate_segment_video(segment, i)
            results.append({
                'segment_id': segment.get('segment_id', i),
                'type': 'narration',
                'start_time': segment.get('start_time', 0),
                'duration': segment.get('duration', 10),
                'video_file': video_file,
                'text': segment.get('narration_text')
            })
        
        print(f"\n{'='*80}")
        print(f"✅ HEYGEN GENERATION COMPLETE")
        print(f"{'='*80}")
        print(f"Generated: {len(results)} videos")
        for r in results:
            if r['video_file']:
                print(f"  - {r['type']}: {Path(r['video_file']).name}")
        print(f"{'='*80}\n")
        
        return results


async def main():
    """Test HeyGen generator"""
    heygen_key = os.getenv('HEYGEN_API_KEY')
    if not heygen_key:
        print("❌ HEYGEN_API_KEY not found")
        return
    
    # Load a script file
    outputs_dir = Path('outputs')
    script_files = sorted(outputs_dir.glob('course_*_script.json'))
    
    if not script_files:
        print("❌ No script files found. Run script_generator.py first.")
        return
    
    script_file = script_files[-1]
    print(f"📂 Loading script: {script_file.name}\n")
    
    with open(script_file) as f:
        script_data = json.load(f)
    
    # Generate videos
    generator = HeyGenGenerator(api_key=heygen_key, output_dir=str(outputs_dir))
    
    # Test with just the intro
    print("Testing with intro segment only...\n")
    intro = [s for s in script_data['segments'] if s.get('segment_type') == 'intro'][0]
    
    video_file = await generator.generate_segment_video(intro, 0)
    
    if video_file:
        print(f"\n✅ Test successful!")
        print(f"   Video: {video_file}")
    else:
        print(f"\n❌ Test failed")


if __name__ == "__main__":
    asyncio.run(main())

