#!/usr/bin/env python3
"""
Advanced Computer Agent Example with Claude Sonnet 3.5
Demonstrates advanced computer vision and AI-powered task automation
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
    """Main example demonstrating advanced computer agent capabilities"""
    
    print("🤖 Advanced PC Agent with Claude Sonnet 3.5")
    print("=" * 50)
    
    # Check if config exists
    config_path = Path(__file__).parent.parent / "config.json"
    if not config_path.exists():
        print("❌ Config file not found!")
        print("Please copy config.example.json to config.json and add your API key")
        return
    
    try:
        # Initialize the agent
        print("🚀 Initializing Computer Agent...")
        agent = ComputerAgent(str(config_path))
        
        # Test Claude API connection
        print("🔗 Testing Claude API connection...")
        test_result = agent.claude_client.test_connection()
        
        if test_result["status"] == "success":
            print("✅ Claude API connected successfully!")
        else:
            print(f"❌ Claude API connection failed: {test_result['message']}")
            return
        
        # Demonstrate advanced capabilities
        demonstrate_screen_analysis(agent)
        demonstrate_web_automation(agent)
        demonstrate_ai_task_planning(agent)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("🧹 Cleaning up...")
        try:
            agent.cleanup()
        except:
            pass


def demonstrate_screen_analysis(agent):
    """Demonstrate advanced screen analysis with Claude vision"""
    print("\n📸 Screen Analysis with Claude Vision")
    print("-" * 40)
    
    try:
        # Capture current screen
        print("📷 Taking screenshot...")
        screenshot = agent.capture_screen()
        
        # Analyze with computer vision
        print("🔍 Analyzing with computer vision...")
        cv_analysis = agent.analyze_screen()
        
        if cv_analysis:
            print(f"👁️  Found {cv_analysis.get('ui_elements_count', 0)} UI elements")
            print(f"📝 Text detected: {cv_analysis.get('has_text', False)}")
            
            # Show dominant colors
            colors = cv_analysis.get('dominant_colors', [])[:3]
            if colors:
                print("🎨 Dominant colors:")
                for i, color in enumerate(colors, 1):
                    print(f"   {i}. {color['hex']} ({color['percentage']:.1f}%)")
        
        # Get Claude's interpretation
        print("🧠 Getting Claude's analysis...")
        # Convert screenshot to bytes for Claude
        import cv2
        from PIL import Image
        import io
        
        # Convert numpy array to PIL Image
        image_pil = Image.fromarray(cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB))
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        image_pil.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        claude_analysis = agent.claude_client.analyze_screenshot(
            img_bytes, 
            "Analyze this screen for interactive elements and current state"
        )
        
        if 'error' not in claude_analysis:
            print("🎯 Claude's insights:")
            if 'current_state' in claude_analysis:
                print(f"   State: {claude_analysis['current_state']}")
            
            elements = claude_analysis.get('elements', [])
            if elements:
                print(f"   Interactive elements found: {len(elements)}")
                for elem in elements[:3]:  # Show first 3
                    print(f"   • {elem.get('type', 'unknown')}: {elem.get('text', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Screen analysis failed: {e}")


def demonstrate_web_automation(agent):
    """Demonstrate intelligent web automation"""
    print("\n🌐 Intelligent Web Automation")
    print("-" * 40)
    
    try:
        # Navigate to a search engine
        print("🔗 Opening web browser...")
        success = agent.navigate_to("https://www.google.com")
        
        if success:
            print("✅ Browser opened successfully")
            
            # Wait a moment for page to load
            time.sleep(2)
            
            # Perform a search using AI planning
            search_query = "artificial intelligence computer vision"
            print(f"🔍 Searching for: {search_query}")
            
            # Use the web automator directly
            if agent.web_search(search_query):
                print("✅ Search completed")
                
                # Take a screenshot of results
                time.sleep(2)
                screenshot_path = "screenshots/search_results.png"
                agent.web_automator.take_screenshot(screenshot_path)
                print(f"📸 Screenshot saved: {screenshot_path}")
                
                # Get page title
                title = agent.web_automator.get_page_title()
                print(f"📄 Page title: {title}")
            else:
                print("❌ Search failed")
        else:
            print("❌ Failed to open browser")
            
    except Exception as e:
        print(f"❌ Web automation failed: {e}")


def demonstrate_ai_task_planning(agent):
    """Demonstrate AI-powered task planning and execution"""
    print("\n🧠 AI Task Planning with Claude")
    print("-" * 40)
    
    try:
        # Example task
        task_description = """
        Take a screenshot of the current screen, analyze it for any text content,
        and create a summary of what's visible on screen
        """
        
        print("📋 Task:", task_description.strip())
        print("🤔 Creating execution plan with Claude...")
        
        # Create task plan
        plan = agent.claude_client.plan_task(task_description)
        
        if 'error' not in plan:
            print("✅ Task plan created!")
            print(f"📊 Steps planned: {len(plan.get('steps', []))}")
            print(f"⏱️  Estimated duration: {plan.get('estimated_duration', 'N/A')}")
            
            # Show the plan steps
            steps = plan.get('steps', [])
            for step in steps[:3]:  # Show first 3 steps
                print(f"   Step {step.get('step_number', '?')}: {step.get('description', 'N/A')}")
            
            # Ask if user wants to execute
            user_input = input("\n🚀 Execute this plan? (y/n): ").lower().strip()
            
            if user_input == 'y':
                print("⚡ Executing task...")
                result = agent.execute_task(task_description)
                
                if result.get('status') == 'completed':
                    print("✅ Task completed successfully!")
                elif result.get('status') == 'partially_completed':
                    completed = result.get('completed_steps', 0)
                    total = result.get('total_steps', 0)
                    print(f"⚠️  Task partially completed ({completed}/{total} steps)")
                else:
                    print(f"❌ Task failed: {result.get('error', 'Unknown error')}")
            else:
                print("🚫 Task execution cancelled")
        else:
            print(f"❌ Failed to create plan: {plan['error']}")
            
    except Exception as e:
        print(f"❌ AI task planning failed: {e}")


if __name__ == "__main__":
    main()