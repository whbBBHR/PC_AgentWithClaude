#!/usr/bin/env python3
"""
Interactive Live Web Automation - Persistent Service Edition
A persistent web automation service that stays running and accepts user commands
Powered by Claude Sonnet 4.5 for intelligent automation guidance.

Usage:
    python interactive_web_automation.py --persistent
    python interactive_web_automation.py --demo
    python interactive_web_automation.py --server
"""

import os
import sys
import json
import time
import asyncio
import threading
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import contextmanager

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text

# Import our automation components
from live_web_automation_enhanced import SafeWebAutomator, AutomationSession

# Load environment
load_dotenv()

console = Console()


class InteractiveWebAutomationService:
    """Persistent web automation service that remains available for user commands"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.automator = None
        self.session = AutomationSession()
        self.running = True
        self.status = "Initialized"
        self.last_action = None
        
    def initialize(self):
        """Initialize the automation service"""
        try:
            console.print("🚀 Initializing Interactive Web Automation Service...", style="bold blue")
            self.automator = SafeWebAutomator(self.config, self.session)
            
            # Initialize the automator
            if not self.automator.initialize():
                raise Exception("Failed to initialize web automator")
            
            self.status = "Ready"
            console.print("✅ Service initialized successfully!", style="green")
            return True
        except Exception as e:
            console.print(f"❌ Failed to initialize: {e}", style="red")
            self.status = f"Error: {e}"
            return False
    
    def get_status_display(self) -> Panel:
        """Get current status display"""
        status_text = Text()
        
        # Service status
        if self.status == "Ready":
            status_text.append("🟢 Service Status: ", style="bold")
            status_text.append("READY", style="bold green")
        elif "Error" in self.status:
            status_text.append("🔴 Service Status: ", style="bold")
            status_text.append(self.status, style="bold red")
        else:
            status_text.append("🟡 Service Status: ", style="bold")
            status_text.append(self.status, style="bold yellow")
        
        status_text.append("\n")
        
        # Session metrics
        if self.session:
            summary = self.session.get_summary()
            status_text.append(f"📊 Actions: {summary['total_actions']} | ")
            status_text.append(f"Errors: {summary['total_errors']} | ")
            status_text.append(f"Success Rate: {summary['success_rate']:.1f}%")
        
        if self.last_action:
            status_text.append(f"\n🕐 Last Action: {self.last_action}")
        
        return Panel(
            status_text,
            title="🌐 Interactive Web Automation Service",
            border_style="blue"
        )
    
    def show_available_commands(self):
        """Display available commands"""
        table = Table(title="📋 Available Commands")
        table.add_column("Command", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Example", style="dim")
        
        commands = [
            ("navigate <url>", "Navigate to a website", "navigate https://example.com"),
            ("search <query>", "Search on DuckDuckGo", "search Python automation"),
            ("find <selector>", "Find element on page", "find input[name='q']"),
            ("click <selector>", "Click an element", "click button.submit"),
            ("type <selector> <text>", "Type text in element", "type input#email hello@example.com"),
            ("screenshot", "Take a screenshot", "screenshot"),
            ("analyze", "Analyze current page", "analyze"),
            ("demo", "Run demo examples", "demo"),
            ("status", "Show service status", "status"),
            ("help", "Show this help", "help"),
            ("quit", "Exit the service", "quit")
        ]
        
        for cmd, desc, example in commands:
            table.add_row(cmd, desc, example)
        
        console.print(table)
    
    def execute_command(self, command: str) -> bool:
        """Execute user command"""
        if not command.strip():
            return True
        
        parts = command.strip().split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        self.last_action = f"{cmd} {' '.join(args)}"
        
        try:
            if cmd == "navigate":
                return self.cmd_navigate(args)
            elif cmd == "search":
                return self.cmd_search(args)
            elif cmd == "find":
                return self.cmd_find(args)
            elif cmd == "click":
                return self.cmd_click(args)
            elif cmd == "type":
                return self.cmd_type(args)
            elif cmd == "screenshot":
                return self.cmd_screenshot()
            elif cmd == "analyze":
                return self.cmd_analyze()
            elif cmd == "demo":
                return self.cmd_demo()
            elif cmd == "status":
                return self.cmd_status()
            elif cmd == "help":
                self.show_available_commands()
                return True
            elif cmd in ["quit", "exit", "stop"]:
                return self.cmd_quit()
            else:
                console.print(f"❌ Unknown command: {cmd}. Type 'help' for available commands.", style="red")
                return True
        except Exception as e:
            console.print(f"❌ Command failed: {e}", style="red")
            return True
    
    def cmd_navigate(self, args: List[str]) -> bool:
        """Navigate to URL"""
        if not args:
            console.print("❌ Usage: navigate <url>", style="red")
            return True
        
        url = args[0]
        console.print(f"🌐 Navigating to {url}...")
        
        if self.automator.navigate_to(url):
            console.print(f"✅ Successfully navigated to {url}", style="green")
        else:
            console.print(f"❌ Failed to navigate to {url}", style="red")
        
        return True
    
    def cmd_search(self, args: List[str]) -> bool:
        """Search on DuckDuckGo"""
        if not args:
            console.print("❌ Usage: search <query>", style="red")
            return True
        
        query = " ".join(args)
        console.print(f"🔍 Searching for: {query}")
        
        # Navigate to DuckDuckGo
        if not self.automator.navigate_to("https://duckduckgo.com"):
            console.print("❌ Failed to reach DuckDuckGo", style="red")
            return True
        
        # Find and use search box
        search_selectors = ["input[name='q']", "input#searchbox_input", "input[type='text']"]
        search_element = self.automator.wait_for_element_advanced(search_selectors, timeout=10)
        
        if not search_element:
            console.print("❌ Search box not found", style="red")
            return True
        
        # Type and submit search
        if self.automator.type_text(search_selectors[0], query):
            if self.automator.press_key(search_selectors[0], "ENTER"):
                console.print(f"✅ Search completed for: {query}", style="green")
            else:
                console.print("❌ Failed to submit search", style="red")
        else:
            console.print("❌ Failed to type search query", style="red")
        
        return True
    
    def cmd_find(self, args: List[str]) -> bool:
        """Find element on page"""
        if not args:
            console.print("❌ Usage: find <selector>", style="red")
            return True
        
        selector = " ".join(args)
        console.print(f"🔍 Looking for element: {selector}")
        
        element = self.automator.find_element(selector)
        if element:
            console.print(f"✅ Element found: {selector}", style="green")
        else:
            console.print(f"❌ Element not found: {selector}", style="red")
        
        return True
    
    def cmd_click(self, args: List[str]) -> bool:
        """Click an element"""
        if not args:
            console.print("❌ Usage: click <selector>", style="red")
            return True
        
        selector = " ".join(args)
        console.print(f"👆 Clicking element: {selector}")
        
        if self.automator.click_element(selector):
            console.print(f"✅ Clicked: {selector}", style="green")
        else:
            console.print(f"❌ Failed to click: {selector}", style="red")
        
        return True
    
    def cmd_type(self, args: List[str]) -> bool:
        """Type text in element"""
        if len(args) < 2:
            console.print("❌ Usage: type <selector> <text>", style="red")
            return True
        
        selector = args[0]
        text = " ".join(args[1:])
        console.print(f"⌨️ Typing '{text}' in: {selector}")
        
        if self.automator.type_text(selector, text):
            console.print(f"✅ Text entered in: {selector}", style="green")
        else:
            console.print(f"❌ Failed to type in: {selector}", style="red")
        
        return True
    
    def cmd_screenshot(self) -> bool:
        """Take a screenshot"""
        console.print("📸 Taking screenshot...")
        
        screenshot_path = self.automator.take_screenshot("user_requested")
        if screenshot_path:
            console.print(f"✅ Screenshot saved: {screenshot_path}", style="green")
        else:
            console.print("❌ Failed to take screenshot", style="red")
        
        return True
    
    def cmd_analyze(self) -> bool:
        """Analyze current page"""
        console.print("🔍 Analyzing current page...")
        
        # Get page info
        if hasattr(self.automator, 'automator') and self.automator.automator and self.automator.automator.driver:
            driver = self.automator.automator.driver
            
            try:
                title = driver.title
                url = driver.current_url
                
                # Count elements
                links = len(driver.find_elements('tag name', 'a'))
                buttons = len(driver.find_elements('tag name', 'button'))
                inputs = len(driver.find_elements('tag name', 'input'))
                forms = len(driver.find_elements('tag name', 'form'))
                
                table = Table(title="📋 Page Analysis")
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="white")
                
                table.add_row("Title", title)
                table.add_row("URL", url)
                table.add_row("Links", str(links))
                table.add_row("Buttons", str(buttons))
                table.add_row("Input Fields", str(inputs))
                table.add_row("Forms", str(forms))
                
                console.print(table)
                
            except Exception as e:
                console.print(f"❌ Analysis failed: {e}", style="red")
        else:
            console.print("❌ No active browser session", style="red")
        
        return True
    
    def cmd_demo(self) -> bool:
        """Run demo examples"""
        console.print("🎭 Running demo examples...")
        
        demos = [
            ("Navigate to Example.com", lambda: self.cmd_navigate(["https://example.com"])),
            ("Search Python automation", lambda: self.cmd_search(["Python", "web", "automation"])),
            ("Take screenshot", lambda: self.cmd_screenshot()),
            ("Analyze page", lambda: self.cmd_analyze())
        ]
        
        for demo_name, demo_func in demos:
            console.print(f"\n🔹 {demo_name}", style="bold blue")
            demo_func()
            time.sleep(2)  # Brief pause between demos
        
        console.print("\n✅ Demo completed!", style="green")
        return True
    
    def cmd_status(self) -> bool:
        """Show service status"""
        console.print(self.get_status_display())
        return True
    
    def cmd_quit(self) -> bool:
        """Quit the service"""
        console.print("👋 Shutting down Interactive Web Automation Service...")
        
        if self.automator:
            self.automator.cleanup()
        
        self.running = False
        self.status = "Stopped"
        console.print("✅ Service stopped successfully", style="green")
        return False
    
    def run_interactive(self):
        """Run interactive command loop"""
        console.clear()
        console.print(Panel.fit(
            "🌐 Interactive Web Automation Service\n" +
            "Powered by Claude Sonnet 4.5\n" +
            "Type 'help' for available commands",
            style="bold blue"
        ))
        
        if not self.initialize():
            return
        
        # Show initial status and help
        console.print(self.get_status_display())
        console.print("\n💡 Type 'demo' to see examples, or 'help' for all commands\n")
        
        while self.running:
            try:
                # Get user command
                command = Prompt.ask(
                    "[bold cyan]web-automation[/bold cyan]",
                    default="help"
                )
                
                # Execute command
                if not self.execute_command(command):
                    break
                    
            except KeyboardInterrupt:
                console.print("\n\n👋 Goodbye!")
                self.cmd_quit()
                break
            except EOFError:
                break


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Interactive Web Automation Service")
    parser.add_argument("--persistent", action="store_true", help="Run persistent interactive service")
    parser.add_argument("--demo", action="store_true", help="Run demo mode")
    parser.add_argument("--config", type=str, help="Config file path", default="config.json")
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        console.print(f"❌ Config file not found: {args.config}", style="red")
        return 1
    except json.JSONDecodeError as e:
        console.print(f"❌ Invalid JSON in config file: {e}", style="red")
        return 1
    
    # Create service
    service = InteractiveWebAutomationService(config)
    
    if args.demo:
        # Run demo mode
        if service.initialize():
            service.cmd_demo()
            service.cmd_quit()
    else:
        # Run interactive mode (default and --persistent)
        service.run_interactive()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())