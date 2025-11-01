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

url = 'https://api.heygen.com/v2/avatars'
headers = {'X-Api-Key': api_key}

print('Fetching available HeyGen avatars...\n')
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    avatars = data.get('data', {}).get('avatars', [])
    
    print(f'Found {len(avatars)} avatars\n')
    
    # Look for 'ray'
    ray_avatars = [a for a in avatars if 'ray' in a.get('avatar_name', '').lower() or 'ray' in a.get('avatar_id', '').lower()]
    
    if ray_avatars:
        print('🎯 Ray-related avatars:')
        for avatar in ray_avatars:
            print(f"  • {avatar.get('avatar_name')} (ID: {avatar.get('avatar_id')})")
        print()
    else:
        print('ℹ️  No avatars with "ray" in the name found.\n')
    
    # Show first 20 avatars
    print('First 20 available avatars:')
    for i, avatar in enumerate(avatars[:20]):
        name = avatar.get('avatar_name', 'Unknown')
        avatar_id = avatar.get('avatar_id', 'Unknown')
        print(f'  {i+1}. {name} (ID: {avatar_id})')
    
    if len(avatars) > 20:
        print(f'  ... and {len(avatars) - 20} more')
    
    print(f'\n💡 Current avatar: Adriana_Business_Front_2_public')
    print(f'   To change it, update self.avatar_id in heygen_generator.py (line 30)')
    
else:
    print(f'❌ API Error: {response.status_code}')
    print(response.text[:500])

