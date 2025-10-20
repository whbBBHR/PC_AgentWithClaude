#!/usr/bin/env python3
"""
DuckDuckGo Live Interaction Test
Test direct interaction with DuckDuckGo search box with visual debugging
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from rich.console import Console

console = Console()

def test_duckduckgo_interaction():
    """Test live interaction with DuckDuckGo search box"""
    
    console.print("🦆 Testing DuckDuckGo Live Interaction", style="bold cyan")
    
    driver = None
    try:
        # Initialize Safari WebDriver
        driver = webdriver.Safari()
        console.print("✅ Safari WebDriver initialized")
        
        # Navigate to DuckDuckGo
        driver.get("https://duckduckgo.com")
        console.print("✅ Navigated to DuckDuckGo")
        
        # Wait for page to fully load
        console.print("⏳ Waiting for page to load...")
        time.sleep(5)
        
        # Try multiple approaches to find and interact with search box
        search_approaches = [
            {
                "name": "Direct CSS Selector",
                "method": lambda: driver.find_element(By.CSS_SELECTOR, "input[name='q']")
            },
            {
                "name": "XPath by Name",
                "method": lambda: driver.find_element(By.XPATH, "//input[@name='q']")
            },
            {
                "name": "XPath by Placeholder", 
                "method": lambda: driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Search')]")
            },
            {
                "name": "WebDriverWait CSS",
                "method": lambda: WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='q']"))
                )
            },
            {
                "name": "WebDriverWait Presence",
                "method": lambda: WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='q']"))
                )
            }
        ]
        
        successful_element = None
        
        for approach in search_approaches:
            console.print(f"\n🔍 Trying: {approach['name']}")
            try:
                element = approach['method']()
                if element:
                    console.print(f"✅ Found element with {approach['name']}")
                    console.print(f"   - Displayed: {element.is_displayed()}")
                    console.print(f"   - Enabled: {element.is_enabled()}")
                    console.print(f"   - Tag: {element.tag_name}")
                    console.print(f"   - Size: {element.size}")
                    console.print(f"   - Location: {element.location}")
                    
                    if element.is_displayed() and element.is_enabled():
                        successful_element = element
                        break
                    
            except Exception as e:
                console.print(f"❌ Failed with {approach['name']}: {e}")
        
        if successful_element:
            console.print(f"\n🎯 Testing interaction with successful element...")
            
            # Clear any existing text
            successful_element.clear()
            console.print("✅ Cleared search box")
            
            # Type search query
            search_query = "Python web automation"
            successful_element.send_keys(search_query)
            console.print(f"✅ Typed: {search_query}")
            
            # Wait to see the typing
            time.sleep(3)
            
            # Press Enter to search
            successful_element.send_keys(Keys.RETURN)
            console.print("✅ Pressed Enter")
            
            # Wait for results
            console.print("⏳ Waiting for search results...")
            time.sleep(5)
            
            # Check if we got to results page
            if "python" in driver.current_url.lower() or "python" in driver.page_source.lower():
                console.print("🎉 Search successful! Results page loaded")
            else:
                console.print("⚠️ Search may not have worked properly")
                
            console.print(f"📍 Current URL: {driver.current_url}")
            console.print(f"📄 Current title: {driver.title}")
            
        else:
            console.print("❌ No working search element found")
            
        # Keep browser open for visual inspection
        console.print("\n👀 Keeping browser open for 15 seconds for visual inspection...")
        time.sleep(15)
        
    except Exception as e:
        console.print(f"❌ Error during test: {e}")
        
    finally:
        if driver:
            driver.quit()
            console.print("🧹 Browser closed")

if __name__ == "__main__":
    test_duckduckgo_interaction()