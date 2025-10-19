#!/usr/bin/env python3
"""
Basic Computer Interaction Example
Demonstrates simple screen interaction capabilities
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from pc_agent import ComputerAgent


def main():
    """Basic computer interaction examples"""
    
    print("🖥️  Basic Computer Interaction Demo")
    print("=" * 40)
    
    # Initialize agent
    config_path = Path(__file__).parent.parent / "config.json"
    
    if not config_path.exists():
        print("❌ Please create config.json from config.example.json")
        return
    
    try:
        agent = ComputerAgent(str(config_path))
        
        print("✅ Agent initialized successfully!")
        print(f"📊 Screen size: {agent.get_screen_info()['primary']}")
        
        # Basic examples
        basic_screen_interaction(agent)
        basic_typing_example(agent)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        try:
            agent.cleanup()
        except:
            pass


def basic_screen_interaction(agent):
    """Demonstrate basic screen interaction"""
    print("\n📸 Screen Interaction")
    print("-" * 25)
    
    try:
        # Take a screenshot
        print("📷 Taking screenshot...")
        screenshot = agent.capture_screen()
        print(f"✅ Screenshot captured: {screenshot.shape}")
        
        # Get screen information
        screen_info = agent.get_screen_info()
        width = screen_info['primary']['width']
        height = screen_info['primary']['height']
        print(f"🖥️  Screen resolution: {width}x{height}")
        
        # Example: Click at center of screen (be careful with this!)
        center_x = width // 2
        center_y = height // 2
        
        user_input = input(f"\n🖱️  Click at center ({center_x}, {center_y})? (y/n): ")
        if user_input.lower() == 'y':
            print("🖱️  Clicking at screen center...")
            agent.click_at(center_x, center_y)
            print("✅ Click executed")
        
    except Exception as e:
        print(f"❌ Screen interaction failed: {e}")


def basic_typing_example(agent):
    """Demonstrate basic typing"""
    print("\n⌨️  Typing Example")
    print("-" * 20)
    
    try:
        text_to_type = input("Enter text to type (or press Enter to skip): ")
        
        if text_to_type.strip():
            print(f"⌨️  Typing: '{text_to_type}'")
            print("⚠️  Make sure cursor is in a text field!")
            
            # Give user time to position cursor
            for i in range(3, 0, -1):
                print(f"Starting in {i}...")
                import time
                time.sleep(1)
            
            agent.type_text(text_to_type)
            print("✅ Text typed successfully!")
        else:
            print("🚫 Typing skipped")
            
    except Exception as e:
        print(f"❌ Typing failed: {e}")


if __name__ == "__main__":
    main()