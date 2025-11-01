"""
Live Recorder - Record Browser-Use live sessions as video
Uses subprocess to open browser and ffmpeg to record
"""

import asyncio
import subprocess
import time
import signal
import os
from pathlib import Path
from typing import Optional
import requests


class LiveSessionRecorder:
    """Record Browser-Use live sessions as MP4 video"""
    
    def __init__(self, output_dir: str = "./outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.recording_process = None
        self.browser_process = None
    
    async def record_session(
        self,
        live_url: str,
        session_id: str,
        course_index: int,
        browser_use_api_key: str,
        estimated_duration: int = 180
    ) -> Optional[str]:
        """
        Record a live session to video file.
        
        Args:
            live_url: The live URL to record
            session_id: Session ID to monitor for completion
            course_index: Course number for filename
            browser_use_api_key: API key to monitor session status
            estimated_duration: Estimated duration in seconds
        
        Returns:
            Path to video file or None if failed
        """
        
        print(f"   🎥 Starting live video recording...")
        print(f"      Live URL: {live_url[:60]}...")
        
        output_file = self.output_dir / f"course_{course_index + 1}_{session_id}_video.mp4"
        
        # Open the live URL in Chrome
        try:
            print(f"      Opening live URL in Chrome...")
            self.browser_process = subprocess.Popen([
                'open',
                '-a', 'Google Chrome',
                '--args',
                '--new-window',
                '--start-fullscreen',
                live_url
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait for browser to load
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"      ⚠️  Failed to open browser: {e}")
            return None
        
        # Start screen recording with ffmpeg (macOS)
        try:
            print(f"      Starting ffmpeg screen recording...")
            
            # macOS screen recording command
            # Capture display 1 (main screen)
            self.recording_process = subprocess.Popen([
                'ffmpeg',
                '-f', 'avfoundation',
                '-framerate', '30',
                '-i', '1',  # Capture display 1
                '-vcodec', 'libx264',
                '-preset', 'ultrafast',
                '-pix_fmt', 'yuv420p',
                '-t', str(estimated_duration + 30),  # Max duration with buffer
                str(output_file)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print(f"      ✅ Recording started to: {output_file.name}")
            
        except Exception as e:
            print(f"      ⚠️  Failed to start recording: {e}")
            self._cleanup_browser()
            return None
        
        # Monitor session for completion
        try:
            await self._monitor_session_completion(
                session_id,
                browser_use_api_key,
                max_wait=estimated_duration + 60
            )
        except Exception as e:
            print(f"      ⚠️  Monitoring error: {e}")
        
        # Stop recording
        self._stop_recording()
        self._cleanup_browser()
        
        # Verify file was created
        if output_file.exists() and output_file.stat().st_size > 1000:
            print(f"      ✅ Video saved: {output_file.name} ({output_file.stat().st_size / 1024 / 1024:.1f} MB)")
            return str(output_file)
        else:
            print(f"      ⚠️  Video file not created or empty")
            return None
    
    async def _monitor_session_completion(
        self,
        session_id: str,
        api_key: str,
        max_wait: int = 300
    ):
        """Monitor session until it's stopped or finished."""
        
        headers = {"X-Browser-Use-API-Key": api_key}
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            await asyncio.sleep(5)
            
            try:
                response = requests.get(
                    f"https://api.browser-use.com/api/v2/sessions/{session_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    session_data = response.json()
                    status = session_data.get('status')
                    
                    if status == 'stopped':
                        print(f"      Session stopped - ending recording")
                        return
                        
            except Exception as e:
                # Continue monitoring even if API call fails
                pass
        
        print(f"      Max wait time reached - ending recording")
    
    def _stop_recording(self):
        """Stop the ffmpeg recording process."""
        if self.recording_process:
            try:
                # Send SIGINT to ffmpeg for clean shutdown
                self.recording_process.send_signal(signal.SIGINT)
                self.recording_process.wait(timeout=10)
                print(f"      Recording stopped")
            except Exception as e:
                # Force kill if graceful shutdown fails
                self.recording_process.kill()
                print(f"      Recording force stopped")
    
    def _cleanup_browser(self):
        """Close the Chrome browser."""
        if self.browser_process:
            try:
                # Close Chrome window
                subprocess.run([
                    'osascript',
                    '-e', 'tell application "Google Chrome" to close (every window whose URL contains "live.browser-use.com")'
                ], timeout=5, capture_output=True)
            except:
                pass


# Test function
async def test_recorder():
    """Test the live recorder with a short session"""
    print("Testing live recorder...")
    print("Note: This requires ffmpeg and Google Chrome to be installed")
    print("      It will record your screen for ~30 seconds\n")
    
    # Create a test session
    api_key = os.getenv('BROWSER_USE_API_KEY')
    
    import requests
    headers = {
        "X-Browser-Use-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Create session
    response = requests.post(
        "https://api.browser-use.com/api/v2/sessions",
        headers=headers,
        json={"startUrl": "https://www.example.com"}
    )
    
    session_data = response.json()
    session_id = session_data['id']
    live_url = session_data['liveUrl']
    
    print(f"Test session created: {session_id}")
    print(f"Live URL: {live_url}\n")
    
    # Record it
    recorder = LiveSessionRecorder(output_dir="./outputs")
    
    video_file = await recorder.record_session(
        live_url=live_url,
        session_id=session_id,
        course_index=999,  # Test course
        browser_use_api_key=api_key,
        estimated_duration=30
    )
    
    if video_file:
        print(f"\n✅ Test recording successful: {video_file}")
    else:
        print(f"\n❌ Test recording failed")
    
    # Cleanup session
    requests.patch(
        f"https://api.browser-use.com/api/v2/sessions/{session_id}",
        headers=headers,
        json={"action": "stop"}
    )


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / '.env')
    
    asyncio.run(test_recorder())

