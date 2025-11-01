"""
Video Composer - Combine HeyGen avatar videos with Browser-Use recordings
Creates final demo videos with intro + picture-in-picture overlay
"""

import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional


class VideoComposer:
    """Compose final videos from HeyGen segments and Browser-Use recordings"""
    
    def __init__(self, output_dir: str = "./outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    async def compose_video(
        self,
        intro_video: str,
        browser_recording: str,
        narration_segments: List[Dict[str, Any]],
        course_index: int,
        session_id: str
    ) -> Optional[str]:
        """
        Compose final video with intro + overlaid narration.
        
        Args:
            intro_video: Path to HeyGen intro video (full screen)
            browser_recording: Path to Browser-Use live recording
            narration_segments: List of narration segment videos with timing
            course_index: Course number
            session_id: Session ID
        
        Returns:
            Path to final composed video
        """
        
        print(f"\n🎬 Composing final video for course {course_index + 1}...")
        
        output_file = self.output_dir / f"course_{course_index + 1}_{session_id}_final.mp4"
        
        # Step 1: Create intro (full screen HeyGen)
        print(f"   📝 Step 1: Processing intro...")
        
        #Step 2: Overlay narration on browser recording
        print(f"   📝 Step 2: Creating picture-in-picture with narration...")
        
        # Build ffmpeg filter complex for:
        # - Intro (full screen)
        # - Then browser recording with avatar overlay in top-right
        
        try:
            await self._compose_with_ffmpeg(
                intro_video,
                browser_recording,
                narration_segments,
                output_file
            )
            
            if output_file.exists():
                file_size_mb = output_file.stat().st_size / 1024 / 1024
                print(f"   ✅ Final video: {output_file.name} ({file_size_mb:.1f} MB)")
                return str(output_file)
            else:
                print(f"   ❌ Video composition failed")
                return None
                
        except Exception as e:
            print(f"   ❌ Composition error: {e}")
            return None
    
    async def _compose_with_ffmpeg(
        self,
        intro_video: str,
        browser_recording: str,
        narration_segments: List[Dict[str, Any]],
        output_file: Path
    ):
        """Use ffmpeg to compose video with picture-in-picture overlays."""
        
        print(f"      Building video composition with PIP overlays...")
        
        # If no narration segments, just concatenate
        if not narration_segments:
            print(f"      No narration segments - simple concatenation")
            await self._simple_concatenate(intro_video, browser_recording, output_file)
            return
        
        # Step 1: Convert browser recording to MP4
        browser_mp4 = self.output_dir / "temp_browser.mp4"
        
        print(f"      Converting browser recording to MP4...")
        convert_cmd = [
            'ffmpeg', '-y', '-i', browser_recording,
            '-c:v', 'libx264', '-preset', 'fast', '-pix_fmt', 'yuv420p',
            str(browser_mp4)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *convert_cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
        )
        await process.wait()
        
        # Step 2: Create video with PIP overlays at specific times
        print(f"      Adding {len(narration_segments)} avatar overlays...")
        
        # Get intro duration from first segment or default
        intro_duration = 12.0  # Default
        # We'll extract this from the actual intro video if needed
        
        # Build complex filter for overlays
        # Each narration segment gets overlaid in top-right at its timestamp
        
        # Check if browser has audio
        browser_has_audio = await self._has_audio_stream(str(browser_mp4))
        
        # Get actual durations for each narration video
        for segment in narration_segments:
            if segment.get('video_file'):
                actual_duration = await self._get_video_duration(segment['video_file'])
                segment['duration'] = actual_duration
        
        filter_complex = self._build_overlay_filter(narration_segments, intro_duration, browser_has_audio)
        
        # Build ffmpeg command with all inputs
        cmd = ['ffmpeg', '-y']
        
        # Input 0: Intro
        cmd.extend(['-i', intro_video])
        
        # Input 1: Browser recording
        cmd.extend(['-i', str(browser_mp4)])
        
        # Inputs 2+: Narration segments
        for segment in narration_segments:
            if segment.get('video_file'):
                cmd.extend(['-i', segment['video_file']])
        
        # Apply filter complex
        cmd.extend(['-filter_complex', filter_complex])
        
        # Output - map both video and audio
        cmd.extend([
            '-map', '[outv]',
            '-map', '[outa]',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-preset', 'fast',
            str(output_file)
        ])
        
        print(f"      Running ffmpeg with overlay filters...")
        
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
        )
        
        await process.wait()
        
        # Cleanup
        if browser_mp4.exists():
            browser_mp4.unlink()
        
        if process.returncode == 0:
            print(f"      ✅ Composition with overlays complete")
        else:
            print(f"      ❌ ffmpeg failed - falling back to simple concatenation")
            await self._simple_concatenate(intro_video, browser_recording, output_file)
    
    def _build_overlay_filter(self, narration_segments: List[Dict[str, Any]], intro_duration: float = 12.0, browser_has_audio: bool = True) -> str:
        """Build ffmpeg filter_complex for PIP overlays with audio."""
        
        # Concatenate intro + browser video and audio into single base timeline
        filters = "[0:v][1:v]concat=n=2:v=1[basev];"
        
        # Audio: if browser has audio, concat it; otherwise just use intro audio
        if browser_has_audio:
            filters += "[0:a][1:a]concat=n=2:v=0:a=1[basea];"
        else:
            filters += "[0:a]acopy[basea];"
        
        # Process each narration segment
        for i, segment in enumerate(narration_segments):
            input_idx = i + 2  # Offset for intro(0) and browser(1)
            
            # Calculate timing
            start = segment.get('start_time', 0) + intro_duration
            duration = segment.get('duration', 5)
            end = start + duration
            start_ms = int(start * 1000)
            
            # Video: scale and shift timestamps to align with overlay window
            filters += f"[{input_idx}:v]scale=320:180,setpts=PTS+{start}/TB[v{i}];"
            
            # Audio: trim to duration, reset timestamps, then delay to sync with video
            filters += f"[{input_idx}:a]atrim=duration={duration},asetpts=PTS-STARTPTS,adelay={start_ms}|{start_ms}[a{i}];"
            
            # Overlay video only during its time window, don't hold last frame
            if i == 0:
                filters += f"[basev][v{i}]overlay=x=W-w-20:y=20:enable='between(t,{start},{end})':eof_action=pass[tmp{i}];"
            else:
                filters += f"[tmp{i-1}][v{i}]overlay=x=W-w-20:y=20:enable='between(t,{start},{end})':eof_action=pass[tmp{i}];"
        
        # Final video output
        last_idx = len(narration_segments) - 1
        filters += f"[tmp{last_idx}]format=yuv420p[outv];"
        
        # Mix base audio with all delayed narration audio tracks
        num_narrations = len(narration_segments)
        narration_audio_inputs = "".join(f"[a{i}]" for i in range(num_narrations))
        filters += f"[basea]{narration_audio_inputs}amix=inputs={1 + num_narrations}:duration=longest[outa]"
        
        return filters
    
    async def _has_audio_stream(self, video_file: str) -> bool:
        """Check if a video file has an audio stream."""
        cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 'a',
            '-show_entries', 'stream=codec_type',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_file
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )
        stdout, _ = await process.communicate()
        
        # If output contains 'audio', the file has an audio stream
        return b'audio' in stdout
    
    async def _get_video_duration(self, video_file: str) -> float:
        """Get the duration of a video file in seconds."""
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_file
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )
        stdout, _ = await process.communicate()
        
        try:
            return float(stdout.decode().strip())
        except (ValueError, AttributeError):
            return 5.0  # Fallback to 5 seconds
    
    async def _simple_concatenate(
        self,
        intro_video: str,
        browser_recording: str,
        output_file: Path
    ):
        """Simple concatenation fallback."""
        
        browser_mp4 = self.output_dir / "temp_browser.mp4"
        
        # Convert if needed
        if not browser_mp4.exists():
            convert_cmd = [
                'ffmpeg', '-y', '-i', browser_recording,
                '-c:v', 'libx264', '-preset', 'fast', '-pix_fmt', 'yuv420p',
                str(browser_mp4)
            ]
            process = await asyncio.create_subprocess_exec(
                *convert_cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
            )
            await process.wait()
        
        # Concatenate
        concat_file = self.output_dir / "concat_list.txt"
        with open(concat_file, 'w') as f:
            f.write(f"file '{Path(intro_video).absolute()}'\n")
            f.write(f"file '{browser_mp4.absolute()}'\n")
        
        cmd = [
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', str(concat_file), '-c', 'copy', str(output_file)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
        )
        await process.wait()
        
        if browser_mp4.exists():
            browser_mp4.unlink()
        if concat_file.exists():
            concat_file.unlink()
    
    async def compose_with_pip_overlay(
        self,
        intro_video: str,
        browser_recording: str,
        avatar_overlays: List[str],
        script: Dict[str, Any],
        output_file: Path
    ):
        """
        Advanced composition with picture-in-picture avatar overlay.
        
        Creates:
        - Intro: Full screen HeyGen avatar
        - Main: Browser recording with avatar in top-right corner
        """
        
        # Get intro duration from script
        intro_duration = script.get('intro_duration', 12)
        
        # Build complex ffmpeg filter for overlay
        # This is a simplified version - full implementation would:
        # 1. Play intro full screen
        # 2. Switch to browser recording
        # 3. Overlay avatar segments at specific timestamps in top-right
        
        overlay_filters = []
        
        # For each narration segment, overlay at specific time
        for segment in script.get('segments', []):
            if segment.get('segment_type') == 'narration':
                start_time = segment.get('start_time', 0)
                duration = segment.get('duration', 5)
                # Would add overlay filter here
        
        print(f"      Building advanced composition...")
        print(f"      (Simplified version - full PIP requires complex ffmpeg)")


async def main():
    """Test video composer"""
    print("Video composer ready!")
    print("Waiting for HeyGen videos to be generated first...")
    print("\nRun heygen_generator.py and wait for videos, then test this.")


if __name__ == "__main__":
    asyncio.run(main())

