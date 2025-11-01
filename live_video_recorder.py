"""
Live Video Recorder - Record Browser-Use live sessions using Playwright
Captures the actual live browser execution as MP4 video
"""

import asyncio
import time
import requests
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright


class LiveVideoRecorder:
    """Record Browser-Use live sessions as video using Playwright"""
    
    def __init__(self, output_dir: str = "./outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    async def record_live_session(
        self,
        live_url: str,
        session_id: str,
        task_id: str,
        course_index: int,
        browser_use_api_key: str,
        estimated_duration: int = 180
    ) -> Optional[str]:
        """
        Record a live Browser-Use session to video.
        
        Args:
            live_url: The live WebSocket URL to record
            session_id: Session ID for filename
            task_id: Task ID to monitor for completion
            course_index: Course number for filename
            browser_use_api_key: API key to monitor task
            estimated_duration: Estimated duration in seconds
        
        Returns:
            Path to recorded video file
        """
        
        print(f"   🎥 Starting live video recording for course {course_index + 1}...")
        
        video_filename = f"course_{course_index + 1}_{session_id}_live.mp4"
        video_path = self.output_dir / video_filename
        
        async with async_playwright() as p:
            # Launch browser with video recording enabled
            browser = await p.chromium.launch(
                headless=False  # Non-headless so we can see it working
            )
            
            # Create context with video recording
            context = await browser.new_context(
                record_video_dir=str(self.output_dir),
                record_video_size={"width": 1280, "height": 720},
                viewport={"width": 1280, "height": 720}
            )
            
            print(f"      Browser launched, opening live URL...")
            
            # Open the live URL
            page = await context.new_page()
            
            try:
                await page.goto(live_url, timeout=30000, wait_until="networkidle")
                print(f"      ✅ Live session loaded")
            except Exception as e:
                print(f"      ⚠️  Failed to load live URL: {e}")
                await context.close()
                await browser.close()
                return None
            
            # Monitor task for completion
            print(f"      📹 Recording in progress (monitoring task completion)...")
            
            await self._monitor_task_completion(
                task_id,
                browser_use_api_key,
                max_wait=estimated_duration + 60
            )
            
            # Get video path before closing (Playwright requirement)
            video_path_from_page = await page.video.path()
            
            # Close page and context (this saves the video)
            await page.close()
            await context.close()
            await browser.close()
            
            print(f"      ✅ Video recording complete")
            
            # Move and rename the video
            if video_path_from_page and Path(video_path_from_page).exists():
                final_path = self.output_dir / video_filename.replace('.mp4', '.webm')
                
                # Move the file
                import shutil
                shutil.move(video_path_from_page, final_path)
                
                file_size_mb = final_path.stat().st_size / 1024 / 1024
                print(f"      ✅ Video saved: {final_path.name} ({file_size_mb:.1f} MB)")
                return str(final_path)
            else:
                print(f"      ⚠️  Video file not created")
                return None
    
    async def _monitor_task_completion(
        self,
        task_id: str,
        api_key: str,
        max_wait: int = 300
    ):
        """Monitor task until it's finished/stopped."""
        
        headers = {"X-Browser-Use-API-Key": api_key}
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            await asyncio.sleep(5)
            
            try:
                response = requests.get(
                    f"https://api.browser-use.com/api/v2/tasks/{task_id}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    task_data = response.json()
                    status = task_data.get('status')
                    
                    elapsed = time.time() - start_time
                    print(f"      [{elapsed:.0f}s] Task status: {status}")
                    
                    if status in ['finished', 'stopped', 'failed']:
                        print(f"      ✅ Task completed ({status})")
                        await asyncio.sleep(3)  # Buffer to capture final frames
                        return
                        
            except Exception as e:
                # Continue monitoring
                pass
        
        print(f"      ⏰ Max recording time reached")


async def test_recorder():
    """Test the live video recorder"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv(Path(__file__).parent.parent / '.env')
    
    api_key = os.getenv('BROWSER_USE_API_KEY')
    if not api_key:
        print("❌ BROWSER_USE_API_KEY not found")
        return
    
    print("="*80)
    print("🎬 TESTING LIVE VIDEO RECORDER")
    print("="*80)
    print("\nCreating test session...")
    
    # Create a short test session
    headers = {
        "X-Browser-Use-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        "https://api.browser-use.com/api/v2/sessions",
        headers=headers,
        json={"startUrl": "https://www.example.com"}
    )
    
    session_data = response.json()
    session_id = session_data['id']
    live_url = session_data['liveUrl']
    
    print(f"✅ Session: {session_id}")
    print(f"📺 Live URL: {live_url}\n")
    
    # Create a quick task
    task_response = requests.post(
        "https://api.browser-use.com/api/v2/tasks",
        headers=headers,
        json={
            "task": "Navigate to example.com and read the page title",
            "sessionId": session_id,
            "llm": "browser-use-llm"
        }
    )
    
    task_id = task_response.json()['id']
    print(f"✅ Task: {task_id}\n")
    
    # Record the session
    recorder = LiveVideoRecorder(output_dir="./outputs")
    
    video_file = await recorder.record_live_session(
        live_url=live_url,
        session_id=session_id,
        task_id=task_id,
        course_index=999,  # Test
        browser_use_api_key=api_key,
        estimated_duration=30
    )
    
    if video_file:
        print(f"\n{'='*80}")
        print(f"✅ TEST SUCCESSFUL!")
        print(f"{'='*80}")
        print(f"Video file: {video_file}")
        print(f"You can play it with: open '{video_file}'")
    else:
        print(f"\n{'='*80}")
        print(f"❌ TEST FAILED")
        print(f"{'='*80}")


if __name__ == "__main__":
    asyncio.run(test_recorder())

