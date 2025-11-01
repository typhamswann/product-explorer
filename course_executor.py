"""
Course Executor - Execute educational demos in parallel and record them
Creates real browser recordings of each generated course
"""

import asyncio
import json
import os
import requests
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from agentmail import AsyncAgentMail
from openai import OpenAI
from live_video_recorder import LiveVideoRecorder

load_dotenv()


class CourseExecutor:
    """Execute educational demos and create recordings"""
    
    def __init__(
        self,
        agentmail_api_key: str,
        browser_use_api_key: str,
        openai_api_key: str,
        output_dir: str = "./outputs"
    ):
        self.agentmail_api_key = agentmail_api_key
        self.browser_use_api_key = browser_use_api_key
        self.openai_api_key = openai_api_key
        self.output_dir = Path(output_dir)
        self.api_base_url = "https://api.browser-use.com/api/v2"
    
    def _generate_password(self) -> str:
        """Generate a random secure password."""
        import random
        import string
        chars = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(random.choice(chars) for _ in range(16))
    
    async def _create_temp_email(self) -> tuple:
        """Create a temporary email inbox."""
        email_client = AsyncAgentMail(api_key=self.agentmail_api_key)
        inbox = await email_client.inboxes.create()
        return email_client, inbox
    
    async def _monitor_verification_email(
        self,
        email_client: AsyncAgentMail,
        inbox: Any,
        timeout: int = 90
    ) -> Optional[str]:
        """Monitor for verification email and extract link."""
        print(f"   📧 Monitoring {inbox.inbox_id} for verification...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            messages = await email_client.inboxes.messages.list(inbox_id=inbox.inbox_id)
            
            if messages.messages:
                latest = messages.messages[0]
                try:
                    full_message = await email_client.inboxes.messages.get(
                        inbox_id=inbox.inbox_id,
                        message_id=latest.message_id
                    )
                    email_body = getattr(full_message, 'text', '') or getattr(full_message, 'html', '') or ""
                except:
                    email_body = getattr(latest, 'preview', '') or ""
                
                # Use GPT-4o to extract verification URL
                try:
                    openai_client = OpenAI(api_key=self.openai_api_key)
                    response = openai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "Extract the email verification URL. Respond with ONLY the URL, nothing else. If no URL, respond 'NONE'."},
                            {"role": "user", "content": f"Subject: {getattr(latest, 'subject', '')}\n\nBody:\n{email_body}"}
                        ],
                        temperature=0,
                        max_tokens=16000
                    )
                    
                    extracted_url = response.choices[0].message.content.strip()
                    if extracted_url and extracted_url != 'NONE' and extracted_url.startswith('http'):
                        print(f"   ✅ Verification link: {extracted_url[:60]}...")
                        return extracted_url
                except Exception as e:
                    print(f"   ⚠️  LLM extraction failed: {e}")
            
            await asyncio.sleep(3)
        
        return None
    
    def _create_session(self, start_url: Optional[str] = None) -> Dict[str, Any]:
        """Create a Browser-Use Cloud session."""
        headers = {
            "X-Browser-Use-API-Key": self.browser_use_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {}
        if start_url:
            payload["startUrl"] = start_url
        
        response = requests.post(
            f"{self.api_base_url}/sessions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def _create_task(
        self,
        task_description: str,
        session_id: str,
        start_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a task in a session."""
        headers = {
            "X-Browser-Use-API-Key": self.browser_use_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "task": task_description,
            "llm": "browser-use-llm",
            "sessionId": session_id
        }
        
        if start_url:
            payload["startUrl"] = start_url
        
        response = requests.post(
            f"{self.api_base_url}/tasks",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def _wait_for_task(self, task_id: str, capture_timeline: bool = True) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Wait for task completion and optionally capture timeline."""
        headers = {"X-Browser-Use-API-Key": self.browser_use_api_key}
        
        timeline_events = []
        start_time = time.time()
        last_step_count = 0
        
        while True:
            await asyncio.sleep(2)  # Poll more frequently for timeline capture
            
            response = requests.get(
                f"{self.api_base_url}/tasks/{task_id}",
                headers=headers
            )
            response.raise_for_status()
            task_data = response.json()
            
            # Capture timeline events
            if capture_timeline:
                steps = task_data.get('steps', [])
                
                # Log new steps since last poll
                for i in range(last_step_count, len(steps)):
                    step = steps[i]
                    t_offset = time.time() - start_time
                    
                    # Extract rich content from step
                    memory = step.get('memory', '')
                    next_goal = step.get('nextGoal', '')
                    eval_previous = step.get('evaluationPreviousGoal', '')
                    actions = step.get('actions', [])
                    screenshot_url = step.get('screenshotUrl', '')
                    
                    event = {
                        'step_number': step.get('number', i + 1),
                        't_offset_s': round(t_offset, 2),
                        't_formatted': self._format_time(t_offset),
                        'url': step.get('url', ''),
                        'screenshot_url': screenshot_url,
                        'memory': memory,
                        'next_goal': next_goal,
                        'evaluation_previous_goal': eval_previous,
                        'actions': actions,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    timeline_events.append(event)
                    
                    # Print useful summary
                    goal_preview = next_goal[:60] if next_goal else 'N/A'
                    print(f"      [{event['t_formatted']}] Step {event['step_number']}: {goal_preview}")
                    if screenshot_url:
                        print(f"          📸 Screenshot: {screenshot_url}")
                
                last_step_count = len(steps)
            
            status = task_data.get('status')
            if status in ['finished', 'stopped', 'failed']:
                return task_data, timeline_events
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS."""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
    
    def _generate_enhanced_script(
        self,
        script_file: Path,
        timeline_data: Dict[str, Any],
        credentials: Dict[str, str]
    ):
        """Generate enhanced script with agent reasoning."""
        from urllib.parse import urlparse
        
        with open(script_file, 'w') as f:
            f.write(f"# {timeline_data['course_title']}\n\n")
            f.write(f"**🎥 Recording:** [{timeline_data['recording_url']}]({timeline_data['recording_url']})\n\n")
            f.write(f"**⏱️  Duration:** {timeline_data['duration_seconds']:.1f} seconds\n\n")
            f.write(f"**📊 Total Steps:** {timeline_data['total_steps']}\n\n")
            
            f.write(f"**🔑 Test Credentials:**\n")
            f.write(f"- Email: `{credentials.get('email', 'N/A')}`\n")
            f.write(f"- Password: `{credentials.get('password', 'N/A')}`\n\n")
            
            f.write("---\n\n")
            f.write("## Detailed Execution Timeline\n\n")
            f.write("*This shows exactly what the AI agent did, including its reasoning at each step.*\n\n")
            
            for event in timeline_data['events']:
                step_num = event.get('step_number', 0)
                time_str = event.get('t_formatted', '00:00')
                url = event.get('url', '')
                memory = event.get('memory', '')
                actions = event.get('actions', [])
                screenshot = event.get('screenshot_url', '')
                
                f.write(f"### [{time_str}] Step {step_num}\n\n")
                
                # URL with path extraction
                if url:
                    parsed = urlparse(url)
                    path = parsed.path or '/'
                    f.write(f"**📍 URL:** `{path}`\n\n")
                    if parsed.query:
                        f.write(f"*Query params: {parsed.query[:60]}...*\n\n")
                
                # Screenshot
                if screenshot:
                    f.write(f"**📸 [Screenshot]({screenshot})**\n\n")
                
                # Agent's reasoning (most important!)
                if memory:
                    f.write(f"**💭 Agent's Plan & Reasoning:**\n\n")
                    f.write(f"{memory}\n\n")
                
                # Actions taken
                if actions:
                    f.write(f"**⚡ Actions Executed:**\n\n")
                    for action_json in actions:
                        try:
                            action_obj = json.loads(action_json)
                            action_type = list(action_obj.keys())[0]
                            action_data = action_obj[action_type]
                            
                            if action_type == 'click':
                                f.write(f"- 🖱️  **Click** element #{action_data.get('index')}\n")
                            elif action_type == 'input':
                                text = action_data.get('text', '')
                                idx = action_data.get('index')
                                # Mask password if it looks like a password field
                                display_text = '***' if len(text) > 12 and any(c in text for c in '!@#$%') else text
                                f.write(f"- ⌨️  **Type** into element #{idx}: `{display_text}`\n")
                            elif action_type == 'scroll':
                                direction = 'down' if action_data.get('down') else 'up'
                                f.write(f"- 📜 **Scroll** {direction}\n")
                            elif action_type == 'wait':
                                secs = action_data.get('seconds', 0)
                                f.write(f"- ⏸️  **Wait** {secs} seconds\n")
                            elif action_type == 'find_text':
                                text = action_data.get('text', '')
                                f.write(f"- 🔍 **Find text:** \"{text}\"\n")
                            elif action_type == 'navigate':
                                nav_url = action_data.get('url', '')
                                f.write(f"- 🧭 **Navigate** to {nav_url}\n")
                            else:
                                f.write(f"- {action_type}: {json.dumps(action_data)}\n")
                        except Exception as e:
                            f.write(f"- Raw: {action_json[:100]}\n")
                    f.write("\n")
                
                f.write("---\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"This course execution took **{timeline_data['duration_seconds']:.1f} seconds** ")
            f.write(f"and completed **{timeline_data['total_steps']} steps**.\n\n")
            f.write(f"Watch the full recording at: {timeline_data['recording_url']}\n")
    
    def _stop_session(self, session_id: str):
        """Stop a session."""
        headers = {
            "X-Browser-Use-API-Key": self.browser_use_api_key,
            "Content-Type": "application/json"
        }
        
        try:
            requests.patch(
                f"{self.api_base_url}/sessions/{session_id}",
                headers=headers,
                json={"action": "stop"}
            )
        except:
            pass
    
    def _get_share_link(self, session_id: str) -> Optional[str]:
        """Get public share link for session."""
        headers = {"X-Browser-Use-API-Key": self.browser_use_api_key}
        
        try:
            response = requests.post(
                f"{self.api_base_url}/sessions/{session_id}/public-share",
                headers=headers
            )
            response.raise_for_status()
            return response.json().get('shareUrl')
        except:
            return None
    
    def _build_course_task(
        self,
        course: Dict[str, Any],
        email: str,
        password: str,
        product_url: str
    ) -> str:
        """Build task description from course implementation."""
        
        from urllib.parse import urlparse
        site_name = urlparse(product_url).netloc
        
        # Extract implementation steps
        impl = course.get('implementation', {})
        starting_point = impl.get('starting_point', 'Home page')
        ui_steps = impl.get('ui_steps', [])
        
        task = f"""
You are demonstrating the course: "{course.get('title', 'Course')}"

IMPORTANT: Stay on {site_name} throughout. Complete this specific course demo.

COURSE OBJECTIVE:
{course.get('key_idea', 'Complete the course')}

STARTING POINT: {starting_point}

STEP-BY-STEP INSTRUCTIONS:
"""
        
        for step in ui_steps:
            step_num = step.get('step_number', 0)
            action = step.get('action', '')
            expected = step.get('expected_result', '')
            
            task += f"""
Step {step_num}: {action}
Expected result: {expected}
"""
        
        task += f"""

CREDENTIALS (if needed):
- Email: {email}
- Password: {password}

EXPECTED OUTCOME:
{impl.get('expected_outcome', 'Course completed successfully')}

Execute each step carefully and verify the expected results.
Provide a summary of what was accomplished.
"""
        
        return task
    
    async def execute_course(
        self,
        course: Dict[str, Any],
        course_index: int,
        product_url: str,
        credentials: Dict[str, str],
        email_client: Any,
        inbox: Any,
        capture_timeline: bool = True
    ) -> Dict[str, Any]:
        """Execute a single course and return recording info."""
        
        course_title = course.get('title', f'Course {course_index + 1}')
        print(f"\n{'='*80}")
        print(f"🎬 Executing Course {course_index + 1}: {course_title}")
        print(f"{'='*80}")
        
        start_time = datetime.now()
        email = credentials['email']
        password = credentials['password']
        
        # Add delay to avoid rate limits
        if course_index > 0:
            delay = course_index * 10  # Stagger by 10 seconds each
            print(f"   ⏸️  Waiting {delay}s to avoid rate limits...")
            await asyncio.sleep(delay)
        
        # Phase 1: Signup session
        print(f"📝 Phase 1: Creating account with {email}...")
        
        signup_session = self._create_session(start_url=product_url)
        signup_session_id = signup_session['id']
        
        print(f"   Session: {signup_session_id}")
        print(f"   Live: {signup_session['liveUrl']}")
        
        # Build signup task
        signup_task_desc = f"""
Sign up for a new account on this website.

Credentials:
- Email: {email}
- Password: {password}

Steps:
1. Find and click the "Sign Up" or "Create Account" button
2. Fill in the signup form with the credentials above
3. Submit the form
4. If asked to verify email, wait on the verification page

Do NOT proceed past the "verify your email" message.
"""
        
        signup_task = self._create_task(signup_task_desc, signup_session_id, product_url)
        print(f"   Task: {signup_task['id']}")
        
        # Create separate email monitoring task (using passed-in email client and inbox)
        email_monitor = asyncio.create_task(
            self._monitor_verification_email(email_client, inbox)
        )
        
        # Wait for signup to complete (no timeline needed for signup)
        print(f"   ⏳ Waiting for signup...")
        signup_result, _ = await self._wait_for_task(signup_task['id'], capture_timeline=False)
        print(f"   ✅ Signup {signup_result['status']}")
        
        # Wait for verification email
        verification_url = await email_monitor
        
        if not verification_url:
            print(f"   ⚠️  No verification email received")
            self._stop_session(signup_session_id)
            return {
                'course_index': course_index,
                'course_title': course_title,
                'status': 'failed',
                'error': 'No verification email',
                'duration': (datetime.now() - start_time).total_seconds()
            }
        
        # Stop signup session
        self._stop_session(signup_session_id)
        
        # Phase 2: Execute course from verification URL
        print(f"\n📚 Phase 2: Executing course demo...")
        
        course_session = self._create_session(start_url=verification_url)
        course_session_id = course_session['id']
        
        print(f"   Session: {course_session_id}")
        print(f"   Live: {course_session['liveUrl']}")
        
        # Build course task
        course_task_desc = self._build_course_task(course, email, password, product_url)
        
        # Add verification handling
        full_task = f"""
STEP 1: Complete email verification
You are starting at the verification URL. Wait for the page to load and verify.

STEP 2: Login if needed
After verification, you may need to login:
- Email: {email}
- Password: {password}

STEP 3: Execute course demo
{course_task_desc}

Complete all steps of the course demonstration.
"""
        
        course_task = self._create_task(full_task, course_session_id, verification_url)
        print(f"   Task: {course_task['id']}")
        
        # Start live video recording
        video_recorder = LiveVideoRecorder(output_dir=str(self.output_dir))
        
        video_recording_task = asyncio.create_task(
            video_recorder.record_live_session(
                live_url=course_session['liveUrl'],
                session_id=course_session_id,
                task_id=course_task['id'],
                course_index=course_index,
                browser_use_api_key=self.browser_use_api_key,
                estimated_duration=120
            )
        )
        
        # Wait for course execution with timeline capture
        print(f"   ⏳ Executing course steps...")
        if capture_timeline:
            print(f"   📊 Capturing timeline events...")
        
        course_result, timeline_events = await self._wait_for_task(course_task['id'], capture_timeline)
        
        # Wait for video recording to complete
        video_file = await video_recording_task
        print(f"   ✅ Course {course_result['status']}")
        
        # Get share link
        share_url = self._get_share_link(course_session_id)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        result = {
            'course_index': course_index,
            'course_title': course_title,
            'status': course_result['status'],
            'duration': duration,
            'session_id': course_session_id,
            'task_id': course_task['id'],
            'share_url': share_url,
            'video_file': video_file,
            'credentials': {
                'email': email,
                'password': password
            },
            'live_url': course_session['liveUrl'],
            'timeline_events': timeline_events if capture_timeline else [],
            'total_steps': len(timeline_events) if capture_timeline else 0
        }
        
        print(f"   ⏱️  Duration: {duration:.1f}s")
        if capture_timeline:
            print(f"   📊 Timeline: {len(timeline_events)} events captured")
        if share_url:
            print(f"   🎥 Share URL: {share_url}")
        if video_file:
            print(f"   📹 Live Video: {Path(video_file).name}")
        
        return result
    
    async def execute_all_courses(
        self,
        demos_data: Dict[str, Any],
        product_url: str
    ) -> List[Dict[str, Any]]:
        """Execute all courses in parallel."""
        
        demos = demos_data.get('demos', [])
        
        print("\n" + "="*80)
        print(f"🎬 COURSE EXECUTOR - Executing {len(demos)} Courses")
        print("="*80)
        print(f"Product: {product_url}")
        print(f"Courses: {len(demos)}")
        print("="*80 + "\n")
        
        # Create credentials and email clients for each course
        tasks = []
        for i, course in enumerate(demos):
            # Create unique email for each course
            email_client = AsyncAgentMail(api_key=self.agentmail_api_key)
            inbox = await email_client.inboxes.create()
            
            credentials = {
                'email': inbox.inbox_id,
                'username': inbox.inbox_id.split('@')[0],
                'password': self._generate_password()
            }
            
            print(f"Course {i+1}: {course.get('title', 'Untitled')}")
            print(f"  Email: {credentials['email']}")
            
            # Create task for this course with email client and inbox
            task = self.execute_course(course, i, product_url, credentials, email_client, inbox, capture_timeline=True)
            tasks.append(task)
        
        print(f"\n🚀 Starting parallel execution of {len(tasks)} courses...\n")
        
        # Execute all courses in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful = []
        failed = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_str = str(result)[:500]
                print(f"❌ Course {i+1} Exception: {error_str[:200]}")
                failed_result = {
                    'course_index': i,
                    'course_title': demos[i].get('title', f'Course {i+1}') if i < len(demos) else f'Course {i+1}',
                    'status': 'exception',
                    'error': error_str,
                    'duration': 0,
                    'timeline_events': []
                }
                failed.append(failed_result)
            elif isinstance(result, dict):
                # Ensure all exception objects are converted to strings
                if 'error' in result and not isinstance(result['error'], str):
                    result['error'] = str(result['error'])[:500]
                
                if result.get('status') == 'finished':
                    successful.append(result)
                else:
                    failed.append(result)
            else:
                failed.append({
                    'course_index': i,
                    'course_title': demos[i].get('title', f'Course {i+1}') if i < len(demos) else f'Course {i+1}',
                    'status': 'unknown',
                    'error': 'Unknown result type',
                    'duration': 0,
                    'timeline_events': []
                })
        
        print("\n" + "="*80)
        print("📊 EXECUTION SUMMARY")
        print("="*80)
        print(f"Total courses: {len(demos)}")
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        print("="*80 + "\n")
        
        return results
    
    def save_execution_results(
        self,
        results: List[Dict[str, Any]],
        demos_data: Dict[str, Any],
        output_dir: Path
    ) -> str:
        """Save execution results to file."""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        from urllib.parse import urlparse
        
        product_url = demos_data.get('product_url', '')
        domain = urlparse(product_url).netloc.replace('.', '_') if product_url else 'unknown'
        
        # Save individual timeline files per course
        for result in results:
            if isinstance(result, dict) and result.get('timeline_events'):
                session_id = result.get('session_id', 'unknown')
                course_idx = result.get('course_index', 0)
                
                timeline_file = output_dir / f"course_{course_idx}_{session_id}_timeline.json"
                
                timeline_data = {
                    'course_index': course_idx,
                    'course_title': result.get('course_title', ''),
                    'session_id': session_id,
                    'task_id': result.get('task_id', ''),
                    'recording_url': result.get('share_url', ''),
                    'duration_seconds': result.get('duration', 0),
                    'total_steps': len(result['timeline_events']),
                    'events': result['timeline_events']
                }
                
                with open(timeline_file, 'w') as f:
                    json.dump(timeline_data, f, indent=2)
                
                # Generate enhanced script with agent reasoning
                script_file = output_dir / f"course_{course_idx}_{session_id}_SCRIPT.md"
                self._generate_enhanced_script(
                    script_file,
                    timeline_data,
                    result.get('credentials', {})
                )
                
                # Add file paths to result
                result['timeline_file'] = str(timeline_file)
                result['script_file'] = str(script_file)
                
                print(f"   📊 Timeline saved: {timeline_file.name}")
                print(f"   📝 Script saved: {script_file.name}")
        
        # Save main execution JSON
        json_file = output_dir / f"course_executions_{domain}_{timestamp}.json"
        
        execution_data = {
            'timestamp': timestamp,
            'product_url': product_url,
            'product_name': demos_data.get('product_name', ''),
            'total_courses': len(results),
            'executions': results
        }
        
        with open(json_file, 'w') as f:
            json.dump(execution_data, f, indent=2)
        
        # Save markdown report
        md_file = output_dir / f"course_executions_{domain}_{timestamp}_REPORT.md"
        
        with open(md_file, 'w') as f:
            f.write("# Course Execution Report\n\n")
            f.write(f"**Product:** {demos_data.get('product_name', 'Unknown')}\n")
            f.write(f"**URL:** {product_url}\n")
            f.write(f"**Executed:** {timestamp}\n\n")
            f.write("---\n\n")
            f.write("## Execution Results\n\n")
            
            for result in results:
                if isinstance(result, dict):
                    title = result.get('course_title', 'Unknown')
                    status = result.get('status', 'unknown')
                    duration = result.get('duration', 0)
                    share_url = result.get('share_url', '')
                    timeline_events = result.get('timeline_events', [])
                    
                    f.write(f"### {title}\n\n")
                    f.write(f"- **Status:** {status}\n")
                    f.write(f"- **Duration:** {duration:.1f}s\n")
                    f.write(f"- **Steps Captured:** {len(timeline_events)}\n")
                    
                    if result.get('credentials'):
                        f.write(f"- **Email:** {result['credentials']['email']}\n")
                        f.write(f"- **Password:** {result['credentials']['password']}\n")
                    
                    if share_url:
                        f.write(f"- **Share URL:** {share_url}\n")
                    
                    if result.get('video_file'):
                        f.write(f"- **Live Video:** `{Path(result['video_file']).name}`\n")
                    
                    if result.get('timeline_file'):
                        f.write(f"- **Timeline:** `{Path(result['timeline_file']).name}`\n")
                    
                    # Add timeline preview with rich data
                    if timeline_events:
                        f.write(f"\n**Timeline Preview (with Agent Plan):**\n\n")
                        
                        # Show first 5 and last 2 events
                        preview_events = timeline_events[:5]
                        if len(timeline_events) > 7:
                            preview_events.append({
                                't_formatted': '...',
                                'step_number': '...',
                                'url': '...',
                                'next_goal': '...'
                            })
                            preview_events.extend(timeline_events[-2:])
                        elif len(timeline_events) > 5:
                            preview_events.extend(timeline_events[5:])
                        
                        for event in preview_events:
                            time_str = event.get('t_formatted', '')
                            step = event.get('step_number', '')
                            url = event.get('url', '')[:60]
                            memory = event.get('memory', '')
                            next_goal = event.get('next_goal', '')
                            actions = event.get('actions', [])
                            screenshot = event.get('screenshot_url', '')
                            
                            f.write(f"**[{time_str}] Step {step}**\n")
                            f.write(f"- URL: {url}\n")
                            
                            # Show agent's plan/reasoning from memory (most valuable!)
                            if memory and memory != '...':
                                # Truncate to first 200 chars for preview
                                plan = memory[:200].replace('\n', ' ')
                                if len(memory) > 200:
                                    plan += '...'
                                f.write(f"- **Agent's Plan:** {plan}\n")
                            
                            # Show actions taken
                            if actions and actions != '...':
                                if len(actions) <= 3:
                                    f.write(f"- **Actions:** {len(actions)} action(s)\n")
                                else:
                                    f.write(f"- **Actions:** {len(actions)} action(s)\n")
                            
                            if screenshot and screenshot != '...':
                                f.write(f"- **Screenshot:** {screenshot}\n")
                            
                            f.write("\n")
                    
                    f.write("\n")
        
        print(f"💾 Execution results saved:")
        print(f"   JSON: {json_file}")
        print(f"   Report: {md_file}\n")
        
        return str(md_file)


async def main():
    """Test course executor."""
    import sys
    
    agentmail_key = os.getenv('AGENTMAIL_API_KEY')
    browser_use_key = os.getenv('BROWSER_USE_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not all([agentmail_key, browser_use_key, openai_key]):
        print("❌ Missing API keys")
        return
    
    # Find latest demos file
    outputs_dir = Path(__file__).parent / "outputs"
    demo_files = sorted(outputs_dir.glob("demos_*.json"))
    
    if not demo_files:
        print("❌ No demo files found. Generate demos first.")
        return
    
    latest_demo_file = demo_files[-1]
    print(f"📂 Loading demos: {latest_demo_file.name}\n")
    
    with open(latest_demo_file, 'r') as f:
        demos_data = json.load(f)
    
    # Option to limit number of courses for testing
    max_courses = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    if max_courses < len(demos_data.get('demos', [])):
        print(f"⚠️  Limiting to first {max_courses} courses for testing\n")
        demos_data['demos'] = demos_data['demos'][:max_courses]
    
    # Get product URL from demos data or exploration
    product_url = ''
    
    # Try to get from demos data first
    if 'product_url' in demos_data:
        product_url = demos_data['product_url']
    
    # If not found, try exploration files
    if not product_url:
        timestamp = latest_demo_file.stem.split('_')[-1]
        domain = '_'.join(latest_demo_file.stem.split('_')[1:-1])
        
        exploration_files = list(outputs_dir.glob(f"exploration_{domain}_*.json"))
        if exploration_files:
            with open(exploration_files[-1], 'r') as f:
                exploration_data = json.load(f)
                product_url = exploration_data.get('product_url', '')
    
    # Last resort: ask user
    if not product_url:
        product_url = input("Enter product URL: ")
    
    # Execute courses
    executor = CourseExecutor(
        agentmail_api_key=agentmail_key,
        browser_use_api_key=browser_use_key,
        openai_api_key=openai_key,
        output_dir=str(outputs_dir)
    )
    
    results = await executor.execute_all_courses(demos_data, product_url)
    
    # Save results
    executor.save_execution_results(results, demos_data, outputs_dir)
    
    print("="*80)
    print("✅ COURSE EXECUTION COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())

