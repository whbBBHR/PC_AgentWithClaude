#!/usr/bin/env python3
"""
Web Automation Example
Demonstrates web browsing and form interaction
"""

import os
import sys
import time
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from pc_agent import ComputerAgent


def main():
    """Web automation examples"""
    
    print("🌐 Web Automation Demo")
    print("=" * 30)
    
    config_path = Path(__file__).parent.parent / "config.json"
    
    if not config_path.exists():
        print("❌ Please create config.json from config.example.json")
        return
    
    try:
        agent = ComputerAgent(str(config_path))
        print("✅ Agent initialized successfully!")
        
        # Web automation examples
        demo_google_search(agent)
        demo_form_interaction(agent)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        try:
            agent.cleanup()
        except:
            pass


def demo_google_search(agent):
    """Demonstrate Google search automation"""
    print("\n🔍 Google Search Demo")
    print("-" * 25)
    
    try:
        # Get search query from user
        query = input("Enter search query (or press Enter for default): ").strip()
        if not query:
            query = "Claude AI computer vision"
        
        print(f"🔗 Opening Google and searching for: '{query}'")
        
        # Navigate to Google
        success = agent.navigate_to("https://www.google.com")
        if not success:
            print("❌ Failed to open Google")
            return
        
        print("✅ Google opened successfully")
        time.sleep(2)  # Wait for page to load
        
        # Perform search
        if agent.web_search(query, "google"):
            print("✅ Search completed!")
            time.sleep(2)
            
            # Take a screenshot
            screenshot_path = f"screenshots/google_search_{int(time.time())}.png"
            if agent.web_automator.take_screenshot(screenshot_path):
                print(f"📸 Screenshot saved: {screenshot_path}")
            
            # Get page title
            title = agent.web_automator.get_page_title()
            print(f"📄 Page title: {title}")
            
            # Click on first result
            user_input = input("\n🖱️  Click on first search result? (y/n): ")
            if user_input.lower() == 'y':
                # Try to click first result
                if agent.web_automator.click_element("h3"):
                    print("✅ Clicked on first result")
                    time.sleep(3)
                    
                    new_title = agent.web_automator.get_page_title()
                    print(f"📄 New page title: {new_title}")
                else:
                    print("❌ Could not click first result")
        else:
            print("❌ Search failed")
            
    except Exception as e:
        print(f"❌ Google search demo failed: {e}")


def demo_form_interaction(agent):
    """Demonstrate form filling"""
    print("\n📝 Form Interaction Demo")
    print("-" * 25)
    
    try:
        # Navigate to a page with forms (using a simple example)
        print("🔗 Opening example form page...")
        
        # Use a simple form page for demonstration
        form_url = "https://httpbin.org/forms/post"
        
        success = agent.navigate_to(form_url)
        if not success:
            print("❌ Failed to open form page")
            return
        
        print("✅ Form page opened")
        time.sleep(2)
        
        # Fill form fields
        form_data = {
            "custname": "John Doe",
            "custtel": "123-456-7890",
            "custemail": "john@example.com"
        }
        
        print("📝 Filling form fields...")
        success = agent.web_automator.fill_form(form_data)
        
        if success:
            print("✅ Form filled successfully!")
            
            # Ask user if they want to submit
            user_input = input("🚀 Submit the form? (y/n): ")
            if user_input.lower() == 'y':
                if agent.web_automator.submit_form():
                    print("✅ Form submitted!")
                    time.sleep(2)
                    
                    # Take screenshot of result
                    screenshot_path = f"screenshots/form_result_{int(time.time())}.png"
                    agent.web_automator.take_screenshot(screenshot_path)
                    print(f"📸 Result screenshot saved: {screenshot_path}")
                else:
                    print("❌ Form submission failed")
            else:
                print("🚫 Form submission cancelled")
        else:
            print("❌ Failed to fill form")
            
    except Exception as e:
        print(f"❌ Form interaction demo failed: {e}")


if __name__ == "__main__":
    main()