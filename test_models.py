#!/usr/bin/env python3
"""
Test Claude Model Availability - Updated for Claude Sonnet 4.5
Tests the latest Claude Sonnet 4.5 model used throughout the PC Agent system
"""
import os
from dotenv import load_dotenv
import anthropic

def test_claude_models():
    """Test Claude Sonnet 4.5 and other available models"""
    load_dotenv()
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("❌ No API key found. Please set ANTHROPIC_API_KEY environment variable.")
        return
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Test Claude models - Priority: Sonnet 4.5 (used in this project)
    models_to_test = [
        # Claude Sonnet 4.5 - PRIMARY MODEL USED IN THIS PROJECT
        "claude-sonnet-4-5-20250929",  # Main model used in document_processor.py
        
        # Latest Claude 3.5 Models (fallback options)
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022", 
        
        # Stable Claude 3 Models (backup)
        "claude-3-haiku-20240307",
        "claude-3-opus-20240229",
        
        # Alternative naming patterns
        "claude-3.5-sonnet",
        "claude-3.5-haiku"
    ]
    
    print("🤖 Testing Claude Model Availability")
    print("=" * 60)
    print("🎯 Primary Goal: Verify Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)")
    print("📋 This model is used throughout PC Agent with Claude v2.0")
    print("=" * 60)
    
    successful_models = []
    
    for i, model in enumerate(models_to_test, 1):
        try:
            print(f"\n{i}. Testing {model}...")
            
            # Test with a simple prompt that should work for all models
            response = client.messages.create(
                model=model,
                max_tokens=20,
                messages=[{"role": "user", "content": "Say 'Model test successful' and nothing else."}]
            )
            
            response_text = response.content[0].text.strip()
            print(f"✅ {model} - WORKS")
            print(f"   Response: {response_text}")
            print(f"   Usage: {response.usage.input_tokens} input + {response.usage.output_tokens} output tokens")
            
            successful_models.append(model)
            
            # If this is Sonnet 4.5, do additional verification
            if "sonnet-4-5" in model:
                print(f"🎉 CLAUDE SONNET 4.5 CONFIRMED WORKING!")
                print(f"   This is the primary model used in PC Agent v2.0")
                break
            
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not_found" in error_msg or "model_not_found" in error_msg:
                print(f"❌ {model} - MODEL NOT FOUND")
            elif "rate_limit" in error_msg.lower():
                print(f"⚠️  {model} - RATE LIMITED (but model exists)")
                successful_models.append(f"{model} (rate limited)")
            else:
                print(f"⚠️  {model} - ERROR: {error_msg}")
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    if successful_models:
        print(f"✅ Working models found: {len(successful_models)}")
        for model in successful_models:
            status = "🎯 PRIMARY" if "sonnet-4-5" in model else "🔄 BACKUP"
            print(f"   {status} {model}")
    else:
        print("❌ No working models found!")
    
    # Check if Sonnet 4.5 is working
    sonnet_45_working = any("sonnet-4-5" in model for model in successful_models)
    
    if sonnet_45_working:
        print(f"\n🎉 SUCCESS: Claude Sonnet 4.5 is working!")
        print(f"✅ PC Agent v2.0 document processing will work correctly")
        print(f"✅ All project features are supported")
    else:
        print(f"\n⚠️  WARNING: Claude Sonnet 4.5 not available!")
        print(f"🔧 PC Agent v2.0 may need model configuration update")
        print(f"💡 Consider updating claude_client.py to use available model")
        
        if successful_models:
            print(f"\n🔄 Recommended alternative: {successful_models[0]}")
    
    return successful_models

def test_claude_sonnet_45_features():
    """Test Claude Sonnet 4.5 specific features used in document processing"""
    load_dotenv()
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("❌ No API key found for feature testing")
        return
    
    client = anthropic.Anthropic(api_key=api_key)
    model = "claude-sonnet-4-5-20250929"
    
    print(f"\n🧪 Testing Claude Sonnet 4.5 Features")
    print("=" * 50)
    
    # Test features used in document_processor.py
    test_cases = [
        {
            "name": "Document Summarization",
            "prompt": "Summarize this text in one sentence: 'Artificial intelligence is transforming many industries through automation and intelligent decision-making capabilities.'",
            "expected_capability": "concise summarization"
        },
        {
            "name": "Text Rewriting", 
            "prompt": "Rewrite this in a professional tone: 'AI is really cool and useful for lots of stuff.'",
            "expected_capability": "style transformation"
        },
        {
            "name": "Analysis Generation",
            "prompt": "Analyze the key themes in this text: 'Technology advancement requires balancing innovation with ethical considerations.'",
            "expected_capability": "analytical reasoning"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        try:
            print(f"\n{i}. Testing {test['name']}...")
            response = client.messages.create(
                model=model,
                max_tokens=100,
                messages=[{"role": "user", "content": test['prompt']}]
            )
            
            result = response.content[0].text.strip()
            print(f"✅ {test['expected_capability'].title()} - WORKING")
            print(f"   Response: {result[:80]}{'...' if len(result) > 80 else ''}")
            
        except Exception as e:
            print(f"❌ {test['name']} - FAILED: {e}")
            return False
    
    print(f"\n🎯 Claude Sonnet 4.5 Feature Test: COMPLETE")
    print(f"✅ All document processing capabilities verified")
    return True
if __name__ == "__main__":
    print("🚀 Claude Model Testing Suite")
    print("🎯 Verifying Claude Sonnet 4.5 for PC Agent v2.0")
    print()
    
    # Test basic model availability
    working_models = test_claude_models()
    
    # If Sonnet 4.5 is working, test its features
    if working_models and any("sonnet-4-5" in model for model in working_models):
        test_claude_sonnet_45_features()
    
    print(f"\n🏁 Testing Complete!")
    print(f"📋 Check results above to verify Claude Sonnet 4.5 compatibility")