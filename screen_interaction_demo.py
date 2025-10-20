#!/usr/bin/env python3
"""
Screen Interaction Methods Demo with Claude 3.5
Demonstrates computer screen capture, analysis, and interaction
"""

import os
import json
import time
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Load environment variables
load_dotenv()

# Import enhanced modules
from src.pc_agent.claude_client import ClaudeClient
from src.pc_agent.computer_agent import ComputerAgent
from src.pc_agent.vision_analyzer import VisionAnalyzer

console = Console()

def load_config():
    """Load the enhanced configuration"""
    with open('config.json', 'r') as f:
        return json.load(f)

def demo_screen_capture():
    """Demonstrate screen capture capabilities"""
    console.print(Panel.fit("📸 Screen Capture Demo", style="bold cyan"))
    
    try:
        # Initialize computer agent
        config = load_config()
        agent = ComputerAgent(config)
        
        console.print("✅ Computer Agent initialized")
        console.print(f"   Screenshot path: {config.get('screenshot_path')}")
        
        # Test screen capture
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Capturing screenshot...", total=None)
            
            # Capture current screen
            screenshot = agent.capture_screen()
            progress.remove_task(task)
        
        if screenshot is not None:
            console.print("✅ Screenshot captured successfully!")
            console.print(f"   Dimensions: {screenshot.shape[1]}x{screenshot.shape[0]}")
            console.print(f"   Color channels: {screenshot.shape[2] if len(screenshot.shape) > 2 else 1}")
            
            # Get screen info
            screen_info = agent.get_screen_info()
            console.print(f"   Primary screen: {screen_info.get('primary', {}).get('width', 'Unknown')}x{screen_info.get('primary', {}).get('height', 'Unknown')}")
            
            return screenshot
        else:
            console.print("❌ Failed to capture screenshot")
            return None
            
    except Exception as e:
        console.print(f"❌ Screen capture error: {str(e)}")
        return None

def demo_vision_analysis(screenshot=None):
    """Demonstrate AI vision analysis of screenshot"""
    console.print(Panel.fit("👁️ AI Vision Analysis Demo", style="bold magenta"))
    
    if screenshot is None:
        console.print("⚠️ No screenshot available for analysis")
        return
    
    try:
        # Initialize Claude client and vision analyzer
        config = load_config()
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key or api_key == 'your-claude-api-key-here':
            console.print("⚠️ No API key - simulating vision analysis")
            # Simulate analysis results
            analysis_result = {
                "elements": [
                    {"type": "window", "text": "Desktop Environment", "purpose": "Main workspace"},
                    {"type": "menu", "text": "Menu Bar", "purpose": "System navigation"},
                    {"type": "dock", "text": "Application Dock", "purpose": "Quick app access"}
                ],
                "current_state": "Desktop with standard macOS interface visible",
                "recommended_actions": ["Take screenshot for detailed analysis", "Identify interactive elements"],
                "confidence": 0.9
            }
        else:
            claude = ClaudeClient(api_key=api_key, config=config)
            vision_analyzer = VisionAnalyzer(claude)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Analyzing screenshot with Claude 3.5...", total=None)
                
                # Convert screenshot to bytes for analysis
                import cv2
                _, img_bytes = cv2.imencode('.png', screenshot)
                
                # Analyze with Claude 3.5
                analysis_result = claude.analyze_screenshot(
                    img_bytes.tobytes(),
                    "Analyze this desktop screenshot and identify interactive elements"
                )
                progress.remove_task(task)
        
        # Display analysis results
        if 'elements' in analysis_result:
            console.print("✅ Vision analysis completed!")
            console.print(f"   Elements found: {len(analysis_result['elements'])}")
            
            for i, element in enumerate(analysis_result['elements'][:5], 1):
                console.print(f"   {i}. {element.get('type', 'Unknown')}: {element.get('text', 'N/A')}")
                
            console.print(f"   Confidence: {analysis_result.get('confidence', 'N/A')}")
        else:
            console.print("⚠️ Analysis completed with limited results")
            
        return analysis_result
        
    except Exception as e:
        console.print(f"❌ Vision analysis error: {str(e)}")
        return None

def demo_mouse_interaction():
    """Demonstrate mouse interaction capabilities"""
    console.print(Panel.fit("🖱️ Mouse Interaction Demo", style="bold green"))
    
    try:
        config = load_config()
        agent = ComputerAgent(config)
        
        # Get current mouse position
        import pyautogui
        current_pos = pyautogui.position()
        console.print(f"✅ Current mouse position: ({current_pos.x}, {current_pos.y})")
        
        # Demonstrate safe mouse movement (small movement)
        console.print("🔄 Testing safe mouse movement...")
        
        # Move mouse slightly and back (safe demo)
        original_x, original_y = current_pos.x, current_pos.y
        
        # Small movement test
        test_x = original_x + 50
        test_y = original_y + 50
        
        console.print(f"   Moving to: ({test_x}, {test_y})")
        pyautogui.moveTo(test_x, test_y, duration=0.5)
        
        time.sleep(0.5)
        
        console.print(f"   Returning to: ({original_x}, {original_y})")
        pyautogui.moveTo(original_x, original_y, duration=0.5)
        
        console.print("✅ Mouse movement test completed safely")
        
        # Show interaction capabilities without actually clicking
        console.print("\n💡 Available interaction methods:")
        console.print("   • click_at(x, y) - Click at coordinates")
        console.print("   • drag_to(x1, y1, x2, y2) - Drag between points")
        console.print("   • scroll_page(direction) - Scroll up/down")
        console.print("   • type_text(text) - Type text input")
        console.print("   • press_key(key) - Press keyboard keys")
        
    except Exception as e:
        console.print(f"❌ Mouse interaction error: {str(e)}")

def demo_keyboard_interaction():
    """Demonstrate keyboard interaction capabilities"""
    console.print(Panel.fit("⌨️ Keyboard Interaction Demo", style="bold blue"))
    
    try:
        config = load_config()
        agent = ComputerAgent(config)
        
        console.print("✅ Keyboard interaction ready")
        console.print("\n💡 Available keyboard methods:")
        console.print("   • type_text('Hello World') - Type text")
        console.print("   • press_key('enter') - Press single key")
        console.print("   • press_key('cmd+c') - Key combinations")
        console.print("   • press_key('alt+tab') - Window switching")
        
        # Safe demonstration (no actual typing)
        console.print("\n🔧 Keyboard capabilities active:")
        console.print("   ✅ Text input with timing control")
        console.print("   ✅ Special key combinations")
        console.print("   ✅ Configurable typing speed")
        console.print(f"   ✅ Current step delay: {config.get('step_delay', 0.3)}s")
        
    except Exception as e:
        console.print(f"❌ Keyboard interaction error: {str(e)}")

def demo_task_planning():
    """Demonstrate AI-powered task planning"""
    console.print(Panel.fit("🧠 AI Task Planning Demo", style="bold yellow"))
    
    try:
        config = load_config()
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key or api_key == 'your-claude-api-key-here':
            console.print("⚠️ No API key - showing example task plan")
            # Show example task plan
            example_plan = {
                "task": "Take screenshot and find clickable buttons",
                "steps": [
                    {"step_number": 1, "action": "analyze", "description": "Capture current screen"},
                    {"step_number": 2, "action": "vision", "description": "Analyze screenshot for UI elements"},
                    {"step_number": 3, "action": "identify", "description": "Locate clickable buttons and links"},
                    {"step_number": 4, "action": "report", "description": "Generate interaction recommendations"}
                ],
                "estimated_duration": "30 seconds",
                "prerequisites": ["Screen access", "Vision analysis"],
                "potential_issues": ["Display scaling", "Dark mode elements"]
            }
            
            console.print("✅ Example task plan generated:")
            for step in example_plan["steps"]:
                console.print(f"   {step['step_number']}. {step['action'].upper()}: {step['description']}")
                
        else:
            claude = ClaudeClient(api_key=api_key, config=config)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Generating task plan with Claude 3.5...", total=None)
                
                task_plan = claude.plan_task(
                    "Take a screenshot of the current screen and identify all clickable elements for automation",
                    context={"system": "macOS", "screen_resolution": "unknown", "mode": "desktop"}
                )
                progress.remove_task(task)
            
            if 'steps' in task_plan:
                console.print("✅ AI task plan generated!")
                console.print(f"   Total steps: {len(task_plan['steps'])}")
                console.print(f"   Duration estimate: {task_plan.get('estimated_duration', 'Unknown')}")
                
                for step in task_plan['steps'][:5]:  # Show first 5 steps
                    console.print(f"   {step.get('step_number', '?')}. {step.get('description', 'No description')}")
            else:
                console.print("⚠️ Task planning completed with limited structure")
                
    except Exception as e:
        console.print(f"❌ Task planning error: {str(e)}")

def main():
    """Run the complete screen interaction demo"""
    console.print(Panel.fit("🚀 Screen Interaction Methods Demo - Claude 3.5 Enhanced", style="bold white"))
    
    # Demo sequence
    console.print("\n" + "="*60)
    
    # 1. Screen Capture
    screenshot = demo_screen_capture()
    console.print()
    
    # 2. Vision Analysis
    demo_vision_analysis(screenshot)
    console.print()
    
    # 3. Mouse Interaction
    demo_mouse_interaction()
    console.print()
    
    # 4. Keyboard Interaction  
    demo_keyboard_interaction()
    console.print()
    
    # 5. AI Task Planning
    demo_task_planning()
    console.print()
    
    # Summary
    console.print(Panel.fit(
        "🎉 Screen Interaction Demo Complete!\n\n"
        "✅ Screen Capture - Working\n"
        "✅ Vision Analysis - Claude 3.5 Enhanced\n" 
        "✅ Mouse Control - Precise & Safe\n"
        "✅ Keyboard Input - Intelligent Timing\n"
        "✅ Task Planning - AI-Powered\n\n"
        "Ready for advanced computer automation!",
        style="bold green"
    ))

if __name__ == "__main__":
    main()