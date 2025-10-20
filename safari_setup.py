#!/usr/bin/env python3
"""
Safari Configuration Helper
Quick setup for Safari web automation
"""

import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

console = Console()

def check_safari_developer_menu():
    """Check if Safari Developer menu is enabled"""
    try:
        result = subprocess.run([
            "defaults", "read", "com.apple.Safari", "IncludeDevelopMenu"
        ], capture_output=True, text=True)
        return result.returncode == 0 and "1" in result.stdout
    except:
        return False

def enable_safari_developer_menu():
    """Enable Safari Developer menu"""
    try:
        subprocess.run([
            "defaults", "write", "com.apple.Safari", "IncludeDevelopMenu", "-bool", "true"
        ], check=True)
        return True
    except:
        return False

def check_safari_automation():
    """Check Safari automation settings"""
    try:
        result = subprocess.run([
            "defaults", "read", "com.apple.Safari", "AllowRemoteAutomation"
        ], capture_output=True, text=True)
        return result.returncode == 0 and "1" in result.stdout
    except:
        return False

def main():
    console.print(Panel.fit("🦁 Safari Web Automation Quick Setup", style="bold cyan"))
    
    console.print("🔍 Checking Safari configuration...")
    
    dev_menu = check_safari_developer_menu()
    automation = check_safari_automation()
    
    console.print(f"   Developer Menu: {'✅ Enabled' if dev_menu else '❌ Disabled'}")
    console.print(f"   Remote Automation: {'✅ Enabled' if automation else '❌ Disabled'}")
    
    if dev_menu and automation:
        console.print("\n🎉 Safari is already configured for automation!")
        console.print("You can run: python live_web_automation.py --live")
        return
    
    console.print("\n🛠️ Safari needs configuration...")
    console.print("This requires manual steps in Safari settings.")
    
    if Confirm.ask("Open Safari settings instructions?"):
        console.print(Panel.fit(
            "🦁 Safari Manual Configuration Steps:\n\n"
            "1. Open Safari browser\n"
            "2. Safari menu → Preferences (or Safari → Settings)\n"
            "3. Click 'Advanced' tab\n"
            "4. Check ☑️ 'Show Develop menu in menu bar'\n"
            "5. Close Preferences\n"
            "6. Develop menu → Allow Remote Automation\n"
            "7. Make sure it's checked ☑️\n\n"
            "Then run: python live_web_automation.py --live",
            style="bold yellow"
        ))
    
    # Try to enable developer menu automatically
    if not dev_menu:
        console.print("\n🔧 Attempting to enable Developer menu automatically...")
        if enable_safari_developer_menu():
            console.print("✅ Developer menu enabled!")
            console.print("   You still need to enable 'Allow Remote Automation'")
        else:
            console.print("❌ Could not enable automatically")
    
    console.print("\n💡 After configuration, Safari web automation will work!")

if __name__ == "__main__":
    main()