#!/usr/bin/env python3
"""
Test Claude Model Availability
"""
import os
from dotenv import load_dotenv
import anthropic

def test_claude_models():
    """Test different Claude model names"""
    load_dotenv()
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("❌ No API key found")
        return
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Test different model names - Current available models
    models_to_test = [
        # Latest Claude 3.5 Models (try current patterns)
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022", 
        # Backup working models
        "claude-3-haiku-20240307",
        "claude-3-opus-20240229",
        # Alternative naming patterns
        "claude-3.5-sonnet",
        "claude-3.5-haiku"
    ]
    
    print("Testing Claude model availability:")
    print("="*50)
    
    for model in models_to_test:
        try:
            print(f"Testing {model}...")
            response = client.messages.create(
                model=model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            print(f"✅ {model} - WORKS")
            print(f"   Response: {response.content[0].text}")
            break
            
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not_found" in error_msg:
                print(f"❌ {model} - NOT FOUND")
            else:
                print(f"⚠️  {model} - ERROR: {error_msg}")
    
    print("\n🔍 Checking available models via API...")
    # Note: Anthropic doesn't have a list models endpoint, so we use trial and error

if __name__ == "__main__":
    test_claude_models()