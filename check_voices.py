import os
import sys
import requests
from pathlib import Path

# Add parent directory to path to load .env
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')

api_key = os.getenv('HEYGEN_API_KEY')
if not api_key:
    print('❌ HEYGEN_API_KEY not found in .env')
    exit(1)

# List voices endpoint
url = 'https://api.heygen.com/v2/voices'
headers = {'X-Api-Key': api_key}

print('Fetching your available voices...\n')
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    
    if data.get('error'):
        print(f"❌ Error: {data['error']}")
        exit(1)
    
    result = data.get('data', {})
    voices = result.get('voices', [])
    
    print(f'Found {len(voices)} voice(s)\n')
    
    # Group by type
    custom_voices = [v for v in voices if v.get('voice_type') == 'custom']
    public_voices = [v for v in voices if v.get('voice_type') == 'public']
    
    if custom_voices:
        print(f"🎤 Your Custom Voices ({len(custom_voices)}):")
        for voice in custom_voices[:20]:
            name = voice.get('display_name', voice.get('name', 'Unnamed'))
            voice_id = voice.get('voice_id')
            gender = voice.get('gender', 'unknown')
            language = voice.get('language', 'unknown')
            print(f"  • {name} ({gender}, {language})")
            print(f"    ID: {voice_id}")
        print()
    
    if public_voices:
        print(f"🌐 Public Voices (showing first 20 of {len(public_voices)}):")
        for voice in public_voices[:20]:
            name = voice.get('display_name', voice.get('name', 'Unnamed'))
            voice_id = voice.get('voice_id')
            gender = voice.get('gender', 'unknown')
            language = voice.get('language', 'unknown')
            print(f"  • {name} ({gender}, {language})")
            print(f"    ID: {voice_id}")
        if len(public_voices) > 20:
            print(f"  ... and {len(public_voices) - 20} more")
    
    print(f"\n💡 Agent avatar's default voice: Xfk8GMWcOK3klRS7h9s3")
    
else:
    print(f'❌ API Error: {response.status_code}')
    print(response.text[:500])

