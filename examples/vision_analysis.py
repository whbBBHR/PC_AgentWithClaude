#!/usr/bin/env python3
"""
Computer Vision Analysis Example
Demonstrates advanced computer vision capabilities with Claude integration
"""

import os
import sys
import json
import time
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from pc_agent import ComputerAgent


def main():
    """Computer vision analysis examples"""
    
    print("👁️  Computer Vision Analysis Demo")
    print("=" * 40)
    
    config_path = Path(__file__).parent.parent / "config.json"
    
    if not config_path.exists():
        print("❌ Please create config.json from config.example.json")
        return
    
    try:
        agent = ComputerAgent(str(config_path))
        print("✅ Agent initialized successfully!")
        
        # Test Claude connection
        test_result = agent.claude_client.test_connection()
        if test_result["status"] != "success":
            print(f"⚠️  Claude API not available: {test_result['message']}")
            print("Some features will be limited...")
        
        # Vision analysis examples
        demo_screen_analysis(agent)
        demo_element_detection(agent)
        demo_claude_vision_analysis(agent)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        try:
            agent.cleanup()
        except:
            pass


def demo_screen_analysis(agent):
    """Demonstrate basic screen analysis"""
    print("\n📸 Basic Screen Analysis")
    print("-" * 30)
    
    try:
        print("📷 Capturing and analyzing screen...")
        
        # Capture screenshot
        screenshot = agent.capture_screen()
        print(f"✅ Screenshot captured: {screenshot.shape}")
        
        # Analyze with computer vision
        analysis = agent.analyze_screen()
        
        if analysis and 'error' not in analysis:
            print("\n📊 Analysis Results:")
            print(f"   🔢 UI elements found: {analysis.get('ui_elements_count', 0)}")
            print(f"   📝 Text detected: {'Yes' if analysis.get('has_text') else 'No'}")
            
            # Show text content
            text_content = analysis.get('text_content', [])
            if text_content:
                print(f"   📄 Text snippets found: {len(text_content)}")
                for i, text_item in enumerate(text_content[:5]):  # Show first 5
                    confidence = text_item.get('confidence', 0)
                    text = text_item.get('text', '')
                    print(f"      {i+1}. '{text}' (confidence: {confidence}%)")
            
            # Show buttons
            buttons = analysis.get('buttons', [])
            if buttons:
                print(f"   🔘 Button-like elements: {len(buttons)}")
                for i, button in enumerate(buttons[:3]):  # Show first 3
                    bbox = button.get('bbox', {})
                    print(f"      {i+1}. Size: {bbox.get('width', 0)}x{bbox.get('height', 0)}")
            
            # Show dominant colors
            colors = analysis.get('dominant_colors', [])
            if colors:
                print(f"   🎨 Dominant colors:")
                for i, color in enumerate(colors[:3]):  # Show top 3
                    print(f"      {i+1}. {color.get('hex', '#000000')} ({color.get('percentage', 0):.1f}%)")
        else:
            error = analysis.get('error', 'Unknown error') if analysis else 'No analysis returned'
            print(f"❌ Analysis failed: {error}")
            
    except Exception as e:
        print(f"❌ Screen analysis failed: {e}")


def demo_element_detection(agent):
    """Demonstrate element detection capabilities"""
    print("\n🔍 Element Detection Demo")
    print("-" * 30)
    
    try:
        print("🔎 Analyzing screen for interactive elements...")
        
        # Get current screen
        screenshot = agent.capture_screen()
        
        # Analyze with vision analyzer
        analysis = agent.vision_analyzer.analyze_image(screenshot)
        
        if analysis and 'error' not in analysis:
            # Show clickable elements
            clickable = analysis.get('clickable_elements', [])
            text_fields = analysis.get('text_fields', [])
            buttons = analysis.get('buttons', [])
            
            print(f"🖱️  Clickable elements: {len(clickable)}")
            print(f"📝 Text fields: {len(text_fields)}")
            print(f"🔘 Buttons: {len(buttons)}")
            
            # Show details of first few elements
            if buttons:
                print("\n🔘 Button Details:")
                for i, button in enumerate(buttons[:3]):
                    bbox = button.get('bbox', {})
                    center = button.get('center', {})
                    print(f"   {i+1}. Position: ({center.get('x', 0)}, {center.get('y', 0)})")
                    print(f"      Size: {bbox.get('width', 0)}×{bbox.get('height', 0)}")
                    print(f"      Area: {button.get('area', 0)} pixels")
            
            if text_fields:
                print("\n📝 Text Field Details:")
                for i, field in enumerate(text_fields[:3]):
                    bbox = field.get('bbox', {})
                    center = field.get('center', {})
                    print(f"   {i+1}. Position: ({center.get('x', 0)}, {center.get('y', 0)})")
                    print(f"      Size: {bbox.get('width', 0)}×{bbox.get('height', 0)}")
        else:
            print("❌ Element detection failed")
            
    except Exception as e:
        print(f"❌ Element detection failed: {e}")


def demo_claude_vision_analysis(agent):
    """Demonstrate Claude's vision analysis capabilities"""
    print("\n🧠 Claude Vision Analysis")
    print("-" * 30)
    
    try:
        if not agent.claude_client.is_available():
            print("❌ Claude API not available - skipping vision analysis")
            return
        
        print("📷 Getting Claude's interpretation of current screen...")
        
        # Capture screenshot
        screenshot = agent.capture_screen()
        
        # Convert to bytes for Claude
        import cv2
        from PIL import Image
        import io
        
        # Convert numpy array to PIL Image
        image_pil = Image.fromarray(cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB))
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        image_pil.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        # Get Claude's analysis
        task_context = input("\nEnter task context (or press Enter for general analysis): ").strip()
        if not task_context:
            task_context = "Analyze this screen for interactive elements and current application state"
        
        print("🤔 Claude is analyzing the screen...")
        analysis = agent.claude_client.analyze_screenshot(img_bytes, task_context)
        
        if analysis and 'error' not in analysis:
            print("\n🎯 Claude's Analysis:")
            
            # Show current state
            if 'current_state' in analysis:
                print(f"📊 Current State: {analysis['current_state']}")
            
            # Show elements found
            elements = analysis.get('elements', [])
            if elements:
                print(f"\n🔍 Interactive Elements ({len(elements)} found):")
                for i, elem in enumerate(elements):
                    elem_type = elem.get('type', 'unknown')
                    text = elem.get('text', 'N/A')
                    purpose = elem.get('purpose', 'N/A')
                    location = elem.get('location', 'N/A')
                    
                    print(f"   {i+1}. {elem_type.title()}")
                    print(f"      Text: '{text}'")
                    print(f"      Purpose: {purpose}")
                    print(f"      Location: {location}")
                    print()
            
            # Show recommended actions
            actions = analysis.get('recommended_actions', [])
            if actions:
                print("💡 Recommended Actions:")
                for i, action in enumerate(actions):
                    print(f"   {i+1}. {action}")
            
            # Show confidence
            confidence = analysis.get('confidence', 0)
            print(f"\n📈 Analysis Confidence: {confidence * 100:.1f}%")
            
        elif 'raw_response' in analysis:
            print("📄 Raw Claude Response:")
            print(analysis['raw_response'])
        else:
            error = analysis.get('error', 'Unknown error') if analysis else 'No response'
            print(f"❌ Claude analysis failed: {error}")
            
    except Exception as e:
        print(f"❌ Claude vision analysis failed: {e}")


if __name__ == "__main__":
    main()