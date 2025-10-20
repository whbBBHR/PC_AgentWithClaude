#!/usr/bin/env python3
"""
Debug API Key Loading
"""
import os
from pathlib import Path

def debug_env_loading():
    print("🔍 Debugging Environment Variable Loading")
    print("="*50)
    
    # Check if .env file exists
    env_file = Path(".env")
    print(f"1. .env file exists: {env_file.exists()}")
    
    if env_file.exists():
        print(f"2. .env file size: {env_file.stat().st_size} bytes")
        
        # Read .env content
        with open(env_file) as f:
            content = f.read()
        
        print(f"3. .env content preview:")
        for i, line in enumerate(content.split('\n')[:10]):
            if line.strip() and not line.startswith('#'):
                if 'ANTHROPIC_API_KEY' in line:
                    key_part = line.split('=')[1] if '=' in line else ''
                    print(f"   Line {i+1}: ANTHROPIC_API_KEY=<{len(key_part)} chars>")
                else:
                    print(f"   Line {i+1}: {line}")
    
    # Check environment variables
    print(f"4. Direct os.environ check:")
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if api_key:
        print(f"   ✅ Found ANTHROPIC_API_KEY ({len(api_key)} chars)")
        print(f"   Starts with: {api_key[:15]}...")
    else:
        print("   ❌ ANTHROPIC_API_KEY not found in os.environ")
    
    # Try manual dotenv loading
    print(f"5. Testing dotenv loading:")
    try:
        from dotenv import load_dotenv
        
        # Load from current directory
        result = load_dotenv()
        print(f"   load_dotenv() result: {result}")
        
        # Check again after loading
        api_key_after = os.environ.get('ANTHROPIC_API_KEY')
        if api_key_after:
            print(f"   ✅ After dotenv: Found key ({len(api_key_after)} chars)")
        else:
            print("   ❌ After dotenv: Still not found")
            
        # Try explicit path
        explicit_result = load_dotenv('.env')
        print(f"   load_dotenv('.env') result: {explicit_result}")
        
    except Exception as e:
        print(f"   ❌ Error loading dotenv: {e}")

if __name__ == "__main__":
    debug_env_loading()