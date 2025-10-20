#!/usr/bin/env python3
"""
Interactive Web Automation Demo Script
Shows how to use the manual interactive shell for real user input

AUTO-DETECTION: Script automatically detects project directory location.
No manual path configuration required!
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def main():
    print("🌐 Interactive Web Automation Demo")
    print("=" * 50)
    print("✅ AUTO-DETECTION: Project path automatically detected!")
    print(f"   📂 Location: {Path(__file__).parent.absolute()}")
    print()
    # Auto-detect current project path
    current_project_path = Path(__file__).parent.absolute()
    
    print("📋 To run the TRULY INTERACTIVE shell where you can type commands:")
    print("   1. Open a terminal")
    print("   2. Navigate to the project directory:")
    print(f"      cd {current_project_path}")
    print("   3. Run the manual interactive shell:")
    print("      python manual_interactive_automation.py")
    print()
    print("🎯 Available Commands You Can Type:")
    print("   • navigate https://example.com")
    print("   • search Python automation")
    print("   • analyze")
    print("   • find input[name='q']")
    print("   • click button.submit")
    print("   • type input#search 'hello world'")
    print("   • screenshot")
    print("   • status")
    print("   • help")
    print("   • quit")
    print()
    print("🚀 Example Interactive Session:")
    print("   🤖 web-automation> navigate https://example.com")
    print("   🌐 Navigating to: https://example.com")
    print("   ✅ Successfully navigated to https://example.com")
    print()
    print("   🤖 web-automation> analyze")
    print("   🔍 Analyzing current page...")
    print("   ✅ Page analysis completed!")
    print()
    print("   🤖 web-automation> search Claude AI")
    print("   🔍 Searching for: Claude AI")
    print("   ✅ Search completed!")
    print()
    print("   🤖 web-automation> quit")
    print("   👋 Goodbye!")
    print()
    print("💡 The shell will:")
    print("   ✅ Stay running until you type 'quit'")
    print("   ✅ Accept your manual input commands")  
    print("   ✅ Provide real-time feedback")
    print("   ✅ Track your session statistics")
    print("   ✅ Use Claude Sonnet 4.5 for AI guidance")
    print()
    
    # Ask if user wants to start interactive mode
    try:
        response = input("🤔 Do you want to start the interactive shell now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            print("🚀 Starting interactive web automation shell...")
            print("   (Type 'quit' to exit when done)")
            print()
            
            # Launch the interactive shell
            # Automatically detect the current project directory
            project_path = Path(__file__).parent.absolute()
            print(f"📂 Using project path: {project_path}")
            
            subprocess.run([
                sys.executable, 
                "manual_interactive_automation.py"
            ], cwd=str(project_path))
        else:
            print("👋 Demo completed. Run the command above when ready!")
    except KeyboardInterrupt:
        print("\n👋 Demo cancelled!")

if __name__ == "__main__":
    main()