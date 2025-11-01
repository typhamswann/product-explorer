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

# List avatar groups endpoint (trying v2)
url = 'https://api.heygen.com/v2/avatar_group.list'
headers = {'X-Api-Key': api_key}
params = {'include_public': 'false'}  # Only show user's custom avatar groups

print('Fetching your avatar groups...\n')
response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    
    if data.get('error'):
        print(f"❌ Error: {data['error']}")
        exit(1)
    
    result = data.get('data', {})
    total_count = result.get('total_count', 0)
    avatar_groups = result.get('avatar_group_list', [])
    
    print(f'Found {total_count} custom avatar group(s)\n')
    
    if avatar_groups:
        for i, group in enumerate(avatar_groups, 1):
            print(f"{i}. {group.get('name', 'Unnamed')}")
            print(f"   ID: {group.get('id')}")
            print(f"   Type: {group.get('group_type')}")
            print(f"   Status: {group.get('train_status')}")
            print(f"   Looks: {group.get('num_looks', 0)}")
            if group.get('default_voice_id'):
                print(f"   Default Voice: {group.get('default_voice_id')}")
            print()
    else:
        print('ℹ️  No custom avatar groups found.')
        print('\nTrying with include_public=true to see all available groups...\n')
        
        # Try again with public avatars
        params['include_public'] = 'true'
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('data', {})
            total_count = result.get('total_count', 0)
            avatar_groups = result.get('avatar_group_list', [])
            
            print(f'Found {total_count} total avatar group(s) (including public)\n')
            
            # Show first 20
            for i, group in enumerate(avatar_groups[:20], 1):
                print(f"{i}. {group.get('name', 'Unnamed')}")
                print(f"   ID: {group.get('id')}")
                print(f"   Type: {group.get('group_type')}")
                if i < 20:
                    print()
            
            if len(avatar_groups) > 20:
                print(f"... and {len(avatar_groups) - 20} more")
    
else:
    print(f'❌ API Error: {response.status_code}')
    print(response.text[:500])

