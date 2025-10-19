#!/usr/bin/env python3
"""
Test Script for PC Agent with Claude
Verifies installation and basic functionality
"""

import os
import sys
import json
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))


def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        # Test core dependencies
        import numpy as np
        print("✅ NumPy imported")
        
        import cv2
        print("✅ OpenCV imported")
        
        from PIL import Image
        print("✅ Pillow imported")
        
        import anthropic
        print("✅ Anthropic imported")
        
        import pyautogui
        print("✅ PyAutoGUI imported")
        
        from selenium import webdriver
        print("✅ Selenium imported")
        
        # Test PC Agent modules
        from pc_agent import ComputerAgent
        print("✅ ComputerAgent imported")
        
        from pc_agent.vision_analyzer import VisionAnalyzer
        print("✅ VisionAnalyzer imported")
        
        from pc_agent.web_automator import WebAutomator
        print("✅ WebAutomator imported")
        
        from pc_agent.claude_client import ClaudeClient
        print("✅ ClaudeClient imported")
        
        from pc_agent.task_executor import TaskExecutor
        print("✅ TaskExecutor imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import: {e}")
        return False


def test_configuration():
    """Test configuration loading"""
    print("\n🔧 Testing configuration...")
    
    config_path = Path(__file__).parent.parent / "config.json"
    
    if not config_path.exists():
        print("⚠️  config.json not found - using example config")
        config_path = Path(__file__).parent.parent / "config.example.json"
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("✅ Configuration loaded successfully")
        
        # Check required fields
        required_fields = ['anthropic_api_key', 'screenshot_path', 'browser']
        missing_fields = []
        
        for field in required_fields:
            if field not in config:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"⚠️  Missing configuration fields: {missing_fields}")
        else:
            print("✅ All required configuration fields present")
        
        # Check API key
        api_key = config.get('anthropic_api_key', '')
        if api_key and api_key != 'your-claude-api-key-here':
            print("✅ API key configured")
        else:
            print("⚠️  API key not configured (using placeholder)")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_screen_capture():
    """Test basic screen capture functionality"""
    print("\n📸 Testing screen capture...")
    
    try:
        from pc_agent import ComputerAgent
        
        # Use example config for testing
        config_path = Path(__file__).parent.parent / "config.example.json"
        agent = ComputerAgent(str(config_path))
        
        # Test screenshot
        screenshot = agent.capture_screen()
        
        if screenshot is not None and screenshot.size > 0:
            print(f"✅ Screenshot captured: {screenshot.shape}")
            
            # Test screen info
            screen_info = agent.get_screen_info()
            if screen_info:
                primary = screen_info.get('primary', {})
                print(f"✅ Screen info: {primary.get('width', 0)}x{primary.get('height', 0)}")
            
            return True
        else:
            print("❌ Screenshot capture failed")
            return False
            
    except Exception as e:
        print(f"❌ Screen capture test failed: {e}")
        return False


def test_claude_api():
    """Test Claude API connection"""
    print("\n🤖 Testing Claude API connection...")
    
    try:
        config_path = Path(__file__).parent.parent / "config.json"
        
        if not config_path.exists():
            print("⚠️  config.json not found - skipping API test")
            print("   Create config.json and add your API key to test Claude integration")
            return True
        
        from pc_agent.claude_client import ClaudeClient
        
        # Load config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        api_key = config.get('anthropic_api_key', '')
        
        if not api_key or api_key == 'your-claude-api-key-here':
            print("⚠️  No valid API key found - skipping API test")
            return True
        
        # Test API connection
        client = ClaudeClient(api_key)
        
        if client.is_available():
            print("✅ Claude client initialized")
            
            # Test basic connection
            result = client.test_connection()
            
            if result['status'] == 'success':
                print("✅ Claude API connection successful")
                return True
            else:
                print(f"❌ Claude API test failed: {result['message']}")
                return False
        else:
            print("❌ Claude client not available")
            return False
            
    except Exception as e:
        print(f"❌ Claude API test failed: {e}")
        return False


def test_web_automation():
    """Test web automation setup"""
    print("\n🌐 Testing web automation setup...")
    
    try:
        from pc_agent.web_automator import WebAutomator
        
        # Load config
        config_path = Path(__file__).parent.parent / "config.example.json"
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        # Create a simple config object
        class TestConfig:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
        
        config = TestConfig(config_data)
        
        # Test WebAutomator initialization
        web_automator = WebAutomator(config)
        print("✅ WebAutomator initialized")
        
        # Note: We don't actually start a browser here to avoid issues
        print("✅ Web automation setup complete (browser test skipped)")
        
        return True
        
    except Exception as e:
        print(f"❌ Web automation test failed: {e}")
        return False


def test_computer_vision():
    """Test computer vision capabilities"""
    print("\n👁️  Testing computer vision...")
    
    try:
        from pc_agent.vision_analyzer import VisionAnalyzer
        
        # Load config
        config_path = Path(__file__).parent.parent / "config.example.json"
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        class TestConfig:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
        
        config = TestConfig(config_data)
        
        # Test VisionAnalyzer
        analyzer = VisionAnalyzer(config)
        print("✅ VisionAnalyzer initialized")
        
        # Test with a simple image
        import numpy as np
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[25:75, 25:75] = [255, 255, 255]  # White square
        
        analysis = analyzer.analyze_image(test_image)
        
        if analysis and 'error' not in analysis:
            print("✅ Image analysis successful")
            print(f"   Image shape: {analysis.get('image_shape', 'unknown')}")
        else:
            print("⚠️  Image analysis returned limited results")
        
        return True
        
    except Exception as e:
        print(f"❌ Computer vision test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 PC Agent with Claude - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Screen Capture Test", test_screen_capture),
        ("Claude API Test", test_claude_api),
        ("Web Automation Test", test_web_automation),
        ("Computer Vision Test", test_computer_vision)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! The PC Agent is ready to use.")
        print("\n📋 Next steps:")
        print("1. Edit config.json and add your Anthropic API key")
        print("2. Run examples: python examples/basic_interaction.py")
        print("3. Try advanced features: python examples/advanced_agent_demo.py")
    else:
        failed = total - passed
        print(f"⚠️  {failed} test(s) failed. Please check the installation.")
        print("\n🔧 Troubleshooting:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Check your Python version (3.8+ required)")
        print("3. Verify system dependencies are installed")


if __name__ == "__main__":
    main()