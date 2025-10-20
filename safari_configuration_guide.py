#!/usr/bin/env python3
"""
Safari Configuration Guide - Step by Step
Complete walkthrough to enable Safari for web automation
Version: 2.0
"""

import os
import sys
import subprocess
import time
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def check_dependencies():
    """Check if required Python packages are installed"""
    try:
        import selenium
        console.print("✅ All dependencies installed")
        return True
    except ImportError as e:
        console.print(f"❌ Missing dependency: selenium")
        console.print("💡 Install with: pip install selenium rich")
        return False

def check_macos_version():
    """Check macOS version for compatibility"""
    try:
        result = subprocess.run(
            ["sw_vers", "-productVersion"],
            capture_output=True,
            text=True
        )
        version = result.stdout.strip()
        console.print(f"ℹ️  macOS version: {version}")
        return version
    except Exception as e:
        console.print(f"⚠️  Cannot determine macOS version: {e}")
        return None

def check_safari_status():
    """Check current Safari configuration status"""
    console.print(Panel.fit("🦁 Safari Configuration Status Check", style="bold cyan"))
    
    # Check if Safari is installed
    safari_path = "/Applications/Safari.app"
    if not os.path.exists(safari_path):
        console.print("❌ Safari not found - please install Safari first")
        return False
    
    console.print("✅ Safari is installed")
    
    # Check if SafariDriver is available
    try:
        result = subprocess.run(["which", "safaridriver"], capture_output=True, text=True)
        if result.returncode == 0:
            console.print("✅ SafariDriver is available")
        else:
            console.print("❌ SafariDriver not found")
            return False
    except FileNotFoundError:
        console.print("❌ Cannot check SafariDriver - command not found")
        return False
    except Exception as e:
        console.print(f"❌ Error checking SafariDriver: {e}")
        return False
    
    # Check Developer Menu setting
    try:
        result = subprocess.run([
            "defaults", "read", "com.apple.Safari", "IncludeDevelopMenu"
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and "1" in result.stdout:
            console.print("✅ Developer Menu is enabled")
        else:
            console.print("❌ Developer Menu is disabled")
    except Exception as e:
        console.print(f"⚠️  Cannot check Developer Menu status: {e}")
    
    return True

def enable_safaridriver():
    """Enable SafariDriver with proper permissions"""
    console.print("\n🔐 Enabling SafariDriver (requires admin password)...")
    try:
        result = subprocess.run(
            ["sudo", "safaridriver", "--enable"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            console.print("✅ SafariDriver enabled successfully")
            return True
        else:
            console.print(f"❌ Failed to enable SafariDriver: {result.stderr}")
            return False
    except FileNotFoundError:
        console.print("❌ SafariDriver command not found")
        return False
    except Exception as e:
        console.print(f"❌ Error enabling SafariDriver: {e}")
        return False

def quick_setup():
    """Attempt automatic setup without user interaction"""
    console.print(Panel.fit("⚡ Quick Setup Mode", style="bold cyan"))
    
    # Enable developer menu
    try:
        subprocess.run([
            "defaults", "write", "com.apple.Safari", 
            "IncludeDevelopMenu", "-bool", "true"
        ], check=True)
        console.print("✅ Developer menu enabled via command")
        
        # Restart Safari to apply changes
        console.print("ℹ️  Please restart Safari to apply changes")
        
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Failed to enable developer menu: {e}")
        return False
    except Exception as e:
        console.print(f"❌ Error during quick setup: {e}")
        return False
    
    console.print("\n⚠️  You still need to manually enable:")
    console.print("   Develop → Allow Remote Automation")
    console.print("   (This cannot be automated for security reasons)")
    
    return True

def show_step_by_step_guide():
    """Show detailed step-by-step Safari configuration"""
    console.print(Panel.fit("📋 Safari Configuration Steps", style="bold green"))
    
    steps = [
        {
            "number": "1️⃣",
            "title": "Open Safari Browser",
            "description": "Launch Safari from Applications folder or Spotlight",
            "action": "Click the Safari icon in your Dock or press Cmd+Space and type 'Safari'"
        },
        {
            "number": "2️⃣", 
            "title": "Open Safari Preferences",
            "description": "Access Safari settings menu",
            "action": "Safari menu → Preferences (or press Cmd+,)"
        },
        {
            "number": "3️⃣",
            "title": "Go to Advanced Tab",
            "description": "Navigate to the Advanced settings section",
            "action": "Click the 'Advanced' tab (rightmost tab in Preferences)"
        },
        {
            "number": "4️⃣",
            "title": "Enable Developer Menu",
            "description": "Show the Develop menu in Safari's menu bar",
            "action": "Check ☑️  'Show Develop menu in menu bar' (at the bottom)"
        },
        {
            "number": "5️⃣",
            "title": "Close Preferences",
            "description": "Save settings and return to Safari",
            "action": "Click the red close button or press Cmd+W"
        },
        {
            "number": "6️⃣",
            "title": "Open Develop Menu",
            "description": "Access the new Develop menu",
            "action": "Look for 'Develop' in Safari's menu bar (between Bookmarks and Window)"
        },
        {
            "number": "7️⃣",
            "title": "Allow Remote Automation",
            "description": "Enable automation control for Safari",
            "action": "Develop → Allow Remote Automation (make sure it's checked ☑️)"
        }
    ]
    
    for step in steps:
        console.print(f"\n{step['number']} {step['title']}")
        console.print(f"   📝 {step['description']}")
        console.print(f"   🎯 Action: {step['action']}")
        
        if not Confirm.ask(f"   Have you completed step {step['number']}?", default=False):
            console.print("   ⏸️  Please complete this step before continuing")
            return False
    
    return True

def test_safari_automation(skip_test=False):
    """Test if Safari automation is working"""
    if skip_test:
        console.print("⏭️  Skipping automation test")
        return True
        
    console.print(Panel.fit("🧪 Testing Safari Automation", style="bold blue"))
    
    console.print("🔄 Testing Safari WebDriver connection...")
    
    # Check if selenium is available
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
    except ImportError:
        console.print("❌ Selenium not installed")
        console.print("💡 Install with: pip install selenium")
        return False
    
    driver = None
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing Safari WebDriver...", total=None)
            
            # Try to create Safari driver
            driver = webdriver.Safari()
            progress.update(task, description="Safari WebDriver started successfully!")
            time.sleep(1)
            
            progress.update(task, description="Testing navigation...")
            driver.get("https://example.com")
            time.sleep(2)
            
            progress.update(task, description="Getting page information...")
            title = driver.title
            url = driver.current_url
            
            progress.remove_task(task)
        
        console.print("✅ Safari automation test successful!")
        console.print(f"   📄 Page title: {title}")
        console.print(f"   🌐 URL: {url}")
        
        time.sleep(3)  # Let user see the result
        
        return True
        
    except Exception as e:
        console.print(f"❌ Safari automation test failed: {str(e)}")
        
        if "Allow remote automation" in str(e) or "remote automation" in str(e).lower():
            console.print("💡 This means step 7 (Allow Remote Automation) needs to be completed")
        elif "Could not establish connection" in str(e):
            console.print("💡 Safari may need to be restarted after enabling settings")
        
        return False
        
    finally:
        if driver:
            try:
                driver.quit()
                console.print("🧹 Browser closed successfully")
            except Exception as e:
                console.print(f"⚠️  Could not close browser cleanly: {e}")

def show_troubleshooting():
    """Show troubleshooting tips"""
    console.print(Panel.fit("🔧 Troubleshooting Safari Automation", style="bold yellow"))
    
    issues = [
        {
            "problem": "Developer Menu not showing",
            "solutions": [
                "Make sure you checked the box in Advanced preferences",
                "Restart Safari after enabling the setting",
                "Check that you're in the correct Advanced tab (not another app's preferences)",
                "Try running: defaults write com.apple.Safari IncludeDevelopMenu -bool true"
            ]
        },
        {
            "problem": "Allow Remote Automation is grayed out",
            "solutions": [
                "Make sure Developer Menu is enabled first",
                "Restart Safari and try again",
                "Check that you're using a recent version of Safari",
                "Run: sudo safaridriver --enable"
            ]
        },
        {
            "problem": "Still getting 'Allow remote automation' error",
            "solutions": [
                "Make sure the checkbox is actually checked (not just clicked)",
                "Try unchecking and rechecking the option",
                "Restart Safari completely (Cmd+Q, then reopen)",
                "Check System Preferences → Security & Privacy → Privacy → Automation",
                "Try disabling and re-enabling the Developer menu"
            ]
        },
        {
            "problem": "SafariDriver not found",
            "solutions": [
                "Run: sudo safaridriver --enable",
                "Check Xcode Command Line Tools are installed: xcode-select --install",
                "Verify Safari is up to date"
            ]
        }
    ]
    
    for issue in issues:
        console.print(f"\n🚨 {issue['problem']}:")
        for solution in issue['solutions']:
            console.print(f"   • {solution}")

def show_alternative_options():
    """Show alternative browser options"""
    console.print(Panel.fit("🌐 Alternative Browser Options", style="bold magenta"))
    
    console.print("If Safari configuration is challenging, consider these alternatives:")
    console.print()
    
    console.print("🥇 Chrome (Recommended)")
    console.print("   • Download: https://www.google.com/chrome/")
    console.print("   • Automatic driver management")
    console.print("   • No configuration needed")
    console.print("   • Best automation compatibility")
    console.print()
    
    console.print("🥈 Firefox")
    console.print("   • Download: https://www.mozilla.org/firefox/")
    console.print("   • Automatic driver management")
    console.print("   • Good privacy features")
    console.print()
    
    console.print("After installing Chrome or Firefox:")
    console.print("   1. Update config.json: change 'browser' to 'chrome' or 'firefox'")
    console.print("   2. Run: python live_web_automation.py --live")

def main():
    """Main Safari configuration guide"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Safari Configuration Guide for Web Automation')
    parser.add_argument('--skip-test', action='store_true', help='Skip the automation test')
    parser.add_argument('--quick', action='store_true', help='Try automatic setup first')
    parser.add_argument('--troubleshoot', action='store_true', help='Show troubleshooting guide only')
    args = parser.parse_args()
    
    console.print(Panel.fit(
        "🦁 Safari Web Automation Configuration Guide\nVersion 2.0", 
        style="bold white"
    ))
    
    # Show troubleshooting only
    if args.troubleshoot:
        show_troubleshooting()
        console.print()
        show_alternative_options()
        return
    
    # Check dependencies first
    if not check_dependencies():
        console.print("\n❌ Please install required dependencies first")
        return
    
    # Check macOS version
    check_macos_version()
    console.print()
    
    # Step 1: Check current status
    if not check_safari_status():
        console.print("\n❌ Safari setup cannot continue")
        console.print("💡 Try running: sudo safaridriver --enable")
        return
    
    console.print()
    
    # Optional: Try quick setup first
    if args.quick or Confirm.ask("Try automatic setup first?", default=True):
        quick_setup()
        console.print()
        if Confirm.ask("Continue with manual verification?", default=True):
            console.print()
        else:
            console.print("⏸️  Setup paused. Run again when ready to test.")
            return
    
    # Step 2: Show step-by-step guide
    if not show_step_by_step_guide():
        console.print("\n⏸️  Configuration paused - continue when ready")
        return
    
    console.print()
    
    # Step 3: Offer to enable SafariDriver
    if Confirm.ask("Enable SafariDriver now? (requires sudo)", default=True):
        enable_safaridriver()
        console.print()
    
    # Step 4: Test automation
    if test_safari_automation(skip_test=args.skip_test):
        console.print(Panel.fit(
            "🎉 Safari Configuration Complete!\n\n"
            "✅ Safari is now ready for web automation\n"
            "✅ Developer menu enabled\n"
            "✅ Remote automation allowed\n"
            "✅ WebDriver test successful\n\n"
            "You can now run:\n"
            "python live_web_automation.py --live",
            style="bold green"
        ))
    else:
        console.print()
        show_troubleshooting()
        console.print()
        show_alternative_options()
        console.print()
        console.print("💡 Run with --troubleshoot flag to see troubleshooting guide only")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n⏸️  Configuration interrupted by user")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n\n❌ Unexpected error: {e}")
        console.print("Please report this issue if it persists")
        sys.exit(1)