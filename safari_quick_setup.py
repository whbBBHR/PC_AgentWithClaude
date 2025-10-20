#!/usr/bin/env python3
"""
Safari Quick Setup - Simple Interactive Guide
"""

import subprocess
import sys

def check_safari_dev_menu():
    """Check if Safari Developer Menu is enabled"""
    try:
        result = subprocess.run([
            "defaults", "read", "com.apple.Safari", "IncludeDevelopMenu"
        ], capture_output=True, text=True)
        
        return result.returncode == 0 and "1" in result.stdout
    except:
        return False

def main():
    print("🦁 Safari Web Automation Setup")
    print("=" * 40)
    
    # Check current status
    dev_menu_enabled = check_safari_dev_menu()
    print(f"Developer Menu: {'✅ Enabled' if dev_menu_enabled else '❌ Disabled'}")
    
    if dev_menu_enabled:
        print("\n🎉 Safari Developer Menu is already enabled!")
        print("Now you just need to enable Remote Automation:")
        print("1. Open Safari")
        print("2. Look for 'Develop' menu in the menu bar")
        print("3. Click Develop → Allow Remote Automation")
        print("4. Make sure it has a checkmark ☑️")
    else:
        print("\n📋 Safari Configuration Steps:")
        print("1. Open Safari browser")
        print("2. Safari menu → Preferences (or Cmd+,)")
        print("3. Click 'Advanced' tab (rightmost)")
        print("4. Check ☑️ 'Show Develop menu in menu bar'")
        print("5. Close Preferences")
        print("6. Develop → Allow Remote Automation")
        print("7. Make sure it's checked ☑️")
    
    print("\n" + "=" * 40)
    
    while True:
        response = input("Have you completed the Safari configuration? (y/n): ").lower().strip()
        
        if response == 'y':
            # Test Safari automation
            print("\n🧪 Testing Safari automation...")
            try:
                from selenium import webdriver
                
                print("🔄 Attempting to start Safari WebDriver...")
                driver = webdriver.Safari()
                print("✅ Safari WebDriver started successfully!")
                
                driver.get("https://example.com")
                print(f"✅ Navigation successful! Page title: {driver.title}")
                
                driver.quit()
                print("✅ Safari automation test complete!")
                print("\n🎉 Safari is now ready for web automation!")
                print("You can run: python live_web_automation.py --live")
                break
                
            except Exception as e:
                print(f"❌ Safari automation test failed: {str(e)}")
                if "Allow remote automation" in str(e):
                    print("💡 You still need to enable 'Allow Remote Automation' in Safari's Develop menu")
                print("Please complete the configuration steps and try again.")
                
        elif response == 'n':
            print("⏸️ Please complete the Safari configuration steps first.")
            print("Run this script again when you're ready to test.")
            sys.exit(0)
        else:
            print("Please enter 'y' or 'n'")

if __name__ == "__main__":
    main()