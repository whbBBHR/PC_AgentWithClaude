#!/usr/bin/env python3
"""
Simple Web Automation Test
This will work once Safari or Chrome is configured
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def test_automation():
    """Simple automation test"""
    
    try:
        # Try Safari first (if configured)
        print("🦁 Attempting Safari...")
        driver = webdriver.Safari()
        print("✅ Safari WebDriver started!")
        
    except Exception as safari_error:
        print(f"❌ Safari failed: {safari_error}")
        print("💡 Configure Safari or install Chrome")
        return False
    
    try:
        # Navigate to a simple page
        print("🌐 Navigating to example.com...")
        driver.get("https://example.com")
        
        # Get page info
        title = driver.title
        url = driver.current_url
        
        print(f"✅ Success!")
        print(f"   Title: {title}")
        print(f"   URL: {url}")
        
        time.sleep(3)  # Let user see the page
        
        return True
        
    except Exception as e:
        print(f"❌ Navigation failed: {e}")
        return False
        
    finally:
        driver.quit()
        print("🧹 Browser closed")

if __name__ == "__main__":
    print("🌐 Web Automation Test")
    print("=" * 30)
    
    success = test_automation()
    
    if success:
        print("\n🎉 Web automation is working!")
        print("Ready to run advanced automation scripts")
    else:
        print("\n⚠️ Setup needed - see web_setup_guide.py")
