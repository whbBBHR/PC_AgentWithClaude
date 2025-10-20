#!/usr/bin/env python3
"""
Enhanced Live Web Automation with Chrome Auto-Detection
Prioritizes Chrome with automatic webdriver management, smart fallbacks
"""

import os
import sys
import json
import time
import platform
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Load environment
load_dotenv()

console = Console()

def detect_and_setup_best_browser():
    """Detect and setup the best available browser for automation"""
    console.print(Panel.fit("🔍 Auto-Detecting Best Browser for Automation", style="bold cyan"))
    
    browsers_to_try = []
    
    # Check Chrome availability
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
    ]
    
    chrome_available = any(os.path.exists(path) for path in chrome_paths)
    
    if chrome_available:
        browsers_to_try.append(("chrome", "Chrome with auto webdriver management"))
        console.print("✅ Chrome detected - will be tried first")
    else:
        console.print("❌ Chrome not found")
        
    # Check Safari (macOS only)
    if platform.system() == "Darwin":
        if os.path.exists("/Applications/Safari.app"):
            browsers_to_try.append(("safari", "Safari (requires manual configuration)"))
            console.print("✅ Safari available (needs configuration)")
        
    # Check Firefox
    firefox_paths = [
        "/Applications/Firefox.app",
        "/usr/bin/firefox",
        "C:/Program Files/Mozilla Firefox/firefox.exe"
    ]
    
    firefox_available = any(os.path.exists(path) for path in firefox_paths)
    if firefox_available:
        browsers_to_try.append(("firefox", "Firefox with auto webdriver management"))
        console.print("✅ Firefox detected")
    else:
        console.print("❌ Firefox not found")
        
    return browsers_to_try

def create_optimized_config(preferred_browser="chrome"):
    """Create optimized configuration for the preferred browser"""
    config = {
        "browser": preferred_browser,
        "headless": False,
        "wait_timeout": 15,  # Longer timeout for reliability
        "max_retries": 5,    # More retries for robustness
        "debug_mode": True,
        "confidence_threshold": 0.8,
        "log_level": "INFO",
        "web_driver_path": "",
        "screenshot_on_error": True,
        "auto_cleanup": True,
        "window_size": {
            "width": 1920,
            "height": 1080
        },
        # Chrome-specific optimizations
        "chrome_options": [
            "--no-sandbox",
            "--disable-dev-shm-usage", 
            "--disable-gpu",
            "--disable-blink-features=AutomationControlled",
            "--disable-extensions",
            "--no-first-run",
            "--disable-default-apps"
        ],
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    return config

def test_browser_automation(browser_type):
    """Test browser automation with the specified browser"""
    console.print(f"🧪 Testing {browser_type} automation...")
    
    try:
        # Import here to avoid issues if selenium not available
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        driver = None
        
        if browser_type == "chrome":
            # Try Chrome with automatic webdriver management
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service as ChromeService
                from selenium.webdriver.chrome.options import Options as ChromeOptions
                
                options = ChromeOptions()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                # Automatic ChromeDriver management
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                
                console.print("✅ Chrome WebDriver initialized with auto-management")
                
            except Exception as chrome_error:
                console.print(f"❌ Chrome setup failed: {chrome_error}")
                return False
                
        elif browser_type == "firefox":
            try:
                from webdriver_manager.firefox import GeckoDriverManager
                from selenium.webdriver.firefox.service import Service as FirefoxService
                from selenium.webdriver.firefox.options import Options as FirefoxOptions
                
                options = FirefoxOptions()
                service = FirefoxService(GeckoDriverManager().install())
                driver = webdriver.Firefox(service=service, options=options)
                
                console.print("✅ Firefox WebDriver initialized with auto-management")
                
            except Exception as firefox_error:
                console.print(f"❌ Firefox setup failed: {firefox_error}")
                return False
                
        elif browser_type == "safari":
            try:
                driver = webdriver.Safari()
                console.print("✅ Safari WebDriver initialized")
                
            except Exception as safari_error:
                console.print(f"❌ Safari setup failed: {safari_error}")
                if "Allow remote automation" in str(safari_error):
                    console.print("💡 Safari needs 'Allow Remote Automation' enabled")
                return False
        
        # Test navigation
        console.print("🌐 Testing navigation to example.com...")
        driver.get("https://example.com")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Get page info
        title = driver.title
        url = driver.current_url
        
        console.print(f"✅ Navigation successful!")
        console.print(f"   Title: {title}")
        console.print(f"   URL: {url}")
        
        # Brief pause to show success
        time.sleep(2)
        
        return True
        
    except Exception as e:
        console.print(f"❌ Browser test failed: {e}")
        return False
        
    finally:
        if driver:
            driver.quit()
            console.print("🧹 Browser closed")

def run_enhanced_automation():
    """Run enhanced web automation with auto-detection"""
    console.print(Panel.fit("🚀 Enhanced Web Automation - Chrome Priority", style="bold green"))
    
    # Detect available browsers
    available_browsers = detect_and_setup_best_browser()
    
    if not available_browsers:
        console.print(Panel.fit(
            "❌ No browsers available for automation\n\n"
            "Install Chrome (recommended):\n"
            "• Download from: https://www.google.com/chrome/\n"
            "• Automatic driver management included\n\n"
            "Or install Firefox:\n"
            "• Download from: https://www.mozilla.org/firefox/",
            style="bold red"
        ))
        return False
    
    console.print(f"\n🎯 Found {len(available_browsers)} browser(s) available")
    
    # Try each browser in order of preference
    for browser_type, description in available_browsers:
        console.print(f"\n🔧 Trying {description}...")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Setting up {browser_type}...", total=None)
            
            success = test_browser_automation(browser_type)
            progress.remove_task(task)
        
        if success:
            console.print(Panel.fit(
                f"🎉 Web Automation Working!\n\n"
                f"✅ Browser: {description}\n"
                f"✅ WebDriver: Auto-managed\n"
                f"✅ Navigation: Successful\n"
                f"✅ Ready for full automation\n\n"
                f"Run live automation with:\n"
                f"python live_web_automation.py --live",
                style="bold green"
            ))
            
            # Update config to use working browser
            config = create_optimized_config(browser_type)
            with open("config.json", "r") as f:
                current_config = json.load(f)
            current_config.update({"browser": browser_type})
            with open("config.json", "w") as f:
                json.dump(current_config, f, indent=4)
            
            console.print(f"✅ Updated config.json to use {browser_type}")
            return True
        else:
            console.print(f"❌ {browser_type} automation failed, trying next option...")
    
    # If we get here, no browsers worked
    console.print(Panel.fit(
        "⚠️ Browser Setup Needed\n\n"
        "Chrome (Recommended):\n"
        "1. Download: https://www.google.com/chrome/\n"
        "2. Install normally\n"
        "3. Run this script again\n\n"
        "Safari (macOS):\n"
        "1. Safari → Preferences → Advanced\n"
        "2. Check 'Show Develop menu'\n"
        "3. Develop → Allow Remote Automation",
        style="bold yellow"
    ))
    
    return False

def demonstrate_chrome_installation():
    """Show Chrome installation demonstration"""
    console.print(Panel.fit("💡 Chrome Installation Guide", style="bold blue"))
    
    console.print("🌐 Why Chrome is recommended:")
    console.print("   ✅ Best automation compatibility")
    console.print("   ✅ Automatic driver management with webdriver-manager")
    console.print("   ✅ No manual configuration needed")
    console.print("   ✅ Fastest and most reliable")
    console.print("   ✅ Works on all platforms (Mac, Windows, Linux)")
    
    console.print("\n📥 Installation steps:")
    if platform.system() == "Darwin":  # macOS
        console.print("   1. Visit: https://www.google.com/chrome/")
        console.print("   2. Download 'Chrome for Mac'")
        console.print("   3. Open .dmg file and drag Chrome to Applications")
        console.print("   4. Run this script again")
        console.print("\n   🍺 Alternative (Homebrew):")
        console.print("   brew install --cask google-chrome")
    else:
        console.print("   1. Visit: https://www.google.com/chrome/")
        console.print("   2. Download Chrome for your system")
        console.print("   3. Install using the downloaded installer")
        console.print("   4. Run this script again")
    
    console.print("\n⚡ After installation:")
    console.print("   • webdriver-manager will auto-download ChromeDriver")
    console.print("   • No additional setup or configuration needed")
    console.print("   • Web automation will work immediately")

def main():
    """Main function"""
    console.print(Panel.fit("🌐 Enhanced Web Automation with Chrome Priority", style="bold white"))
    
    # Check if this is a test run
    if "--test" in sys.argv:
        success = run_enhanced_automation()
        return
    
    # Show Chrome installation info
    demonstrate_chrome_installation()
    console.print()
    
    # Try to run automation
    success = run_enhanced_automation()
    
    if not success:
        console.print()
        console.print(Panel.fit(
            "🎯 Next Steps:\n\n"
            "1. Install Chrome (recommended) or configure Safari\n"
            "2. Run: python enhanced_web_automation.py --test\n"
            "3. Then: python live_web_automation.py --live\n\n"
            "Demo mode (works now): python web_automation_demo.py",
            style="cyan"
        ))

if __name__ == "__main__":
    main()