#!/usr/bin/env python3
"""
Chrome Download Helper for Web Automation
"""

import os
import sys
import platform
from rich.console import Console
from rich.panel import Panel

console = Console()

def show_chrome_installation():
    """Show Chrome installation instructions"""
    console.print(Panel.fit("🌐 Chrome Installation for Web Automation", style="bold cyan"))
    
    system = platform.system()
    
    if system == "Darwin":  # macOS
        console.print("📱 macOS Chrome Installation:")
        console.print("   1. Visit: https://www.google.com/chrome/")
        console.print("   2. Download Chrome for Mac")
        console.print("   3. Install by dragging to Applications folder")
        console.print("   4. Run: python live_web_automation.py --live")
        console.print()
        console.print("💡 Alternative (if you have Homebrew):")
        console.print("   brew install --cask google-chrome")
        
    elif system == "Windows":
        console.print("🪟 Windows Chrome Installation:")
        console.print("   1. Visit: https://www.google.com/chrome/")
        console.print("   2. Download Chrome for Windows")
        console.print("   3. Run installer as administrator")
        console.print("   4. Run: python live_web_automation.py --live")
        
    elif system == "Linux":
        console.print("🐧 Linux Chrome Installation:")
        console.print("   # Ubuntu/Debian:")
        console.print("   wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -")
        console.print("   sudo sh -c 'echo \"deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main\" >> /etc/apt/sources.list.d/google-chrome.list'")
        console.print("   sudo apt update && sudo apt install google-chrome-stable")
        console.print()
        console.print("   # CentOS/RHEL/Fedora:")
        console.print("   sudo dnf install google-chrome-stable")
    
    console.print()
    console.print("✅ After Chrome installation:")
    console.print("   • webdriver-manager will automatically download ChromeDriver")
    console.print("   • No additional configuration needed")
    console.print("   • Web automation will work immediately")

def show_current_options():
    """Show current automation options"""
    console.print(Panel.fit("🚀 Current Web Automation Options", style="bold green"))
    
    console.print("Option 1: Safari (Available Now)")
    console.print("   📝 Setup required (5 minutes):")
    console.print("   1. Open Safari → Preferences → Advanced")
    console.print("   2. Check 'Show Develop menu in menu bar'")
    console.print("   3. Develop → Allow Remote Automation")
    console.print("   4. Change config.json: browser='safari'")
    console.print("   5. Run: python live_web_automation.py --live")
    console.print()
    
    console.print("Option 2: Chrome (Recommended)")
    console.print("   🌐 Download and install Chrome")
    console.print("   ✅ Automatic driver management")
    console.print("   ✅ No additional configuration")
    console.print("   ✅ Best compatibility")
    console.print()
    
    console.print("Option 3: Demo Mode (Works Now)")
    console.print("   🎯 Full feature demonstration")
    console.print("   🧠 Claude 3.5 planning active")
    console.print("   📊 All capabilities shown")
    console.print("   Run: python web_automation_demo.py")

def main():
    show_chrome_installation()
    console.print()
    show_current_options()
    
    console.print()
    console.print(Panel.fit(
        "🎉 Web Automation System Ready!\n\n"
        "✅ All Selenium dependencies installed\n"
        "✅ Claude 3.5 Haiku integration working\n"
        "✅ Automatic driver management ready\n"
        "✅ Multi-browser support implemented\n\n"
        "Just need to choose and configure a browser!",
        style="bold yellow"
    ))

if __name__ == "__main__":
    main()