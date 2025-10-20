#!/usr/bin/env python3
"""
DuckDuckGo Visual Browser Inspection
Opens DuckDuckGo in Safari and keeps it open for visual inspection
"""

import time
from selenium import webdriver
from rich.console import Console

console = Console()

def show_duckduckgo_in_browser():
    """Open DuckDuckGo and keep browser window open for visual inspection"""
    
    console.print("🦆 Opening DuckDuckGo in Safari for Visual Inspection", style="bold cyan")
    
    driver = None
    try:
        # Initialize Safari WebDriver
        console.print("🚀 Starting Safari WebDriver...")
        driver = webdriver.Safari()
        console.print("✅ Safari browser opened")
        
        # Navigate to DuckDuckGo
        console.print("🌐 Navigating to DuckDuckGo...")
        driver.get("https://duckduckgo.com")
        console.print("✅ DuckDuckGo loaded")
        
        # Visual inspection period
        console.print("\n" + "="*60)
        console.print("👀 [bold yellow]VISUAL INSPECTION TIME[/bold yellow]")
        console.print("📍 The Safari browser window is now open with DuckDuckGo")
        console.print("🔍 Look for the search box in the browser window")
        console.print("📝 Check if you can see:")
        console.print("   • DuckDuckGo logo")
        console.print("   • Search input box")
        console.print("   • 'Search privately' placeholder text")
        console.print("   • Any other page elements")
        console.print("="*60)
        
        # Keep browser open for extended inspection
        for countdown in range(30, 0, -5):
            console.print(f"⏰ Browser will stay open for {countdown} more seconds...")
            time.sleep(5)
        
        console.print("📸 Taking final screenshot...")
        driver.save_screenshot("screenshots/duckduckgo_final_view.png")
        console.print("✅ Screenshot saved: screenshots/duckduckgo_final_view.png")
        
    except Exception as e:
        console.print(f"❌ Error: {e}")
        
    finally:
        if driver:
            console.print("🧹 Closing browser in 5 seconds...")
            time.sleep(5)
            driver.quit()
            console.print("✅ Browser closed")

if __name__ == "__main__":
    show_duckduckgo_in_browser()