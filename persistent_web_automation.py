#!/usr/bin/env python3
"""
Persistent Web Automation Shell
A command-line interface that stays running and accepts user automation commands
Powered by Claude Sonnet 4.5 for intelligent automation guidance.
"""

import os
import sys
import json
import time
import cmd
from typing import Optional, Dict, Any, List
from datetime import datetime

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm

# Import our automation components
from src.pc_agent.web_automator import WebAutomator
from src.pc_agent.claude_client import ClaudeClient

# Load environment
load_dotenv()

console = Console()


class WebAutomationShell(cmd.Cmd):
    """Interactive shell for web automation commands"""
    
    intro = """
╭─────────────────────────────────────────────────────────────╮
│ 🌐 Persistent Web Automation Shell - Claude Sonnet 4.5     │
│                                                             │
│ A persistent service for interactive web automation.        │
│ Type 'help' for available commands or 'demo' for examples. │
╰─────────────────────────────────────────────────────────────╯
    """
    
    prompt = '🤖 web-automation> '
    
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.automator = None
        self.claude = None
        self.session_start = datetime.now()
        self.actions_performed = 0
        self.successful_actions = 0
        
        # Initialize services
        self.initialize_services()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            console.print("❌ Config file not found, using defaults", style="yellow")
            return {
                "browser": "safari",
                "headless": False,
                "wait_timeout": 10,
                "debug_mode": True
            }
    
    def initialize_services(self):
        """Initialize web automation and Claude services"""
        try:
            console.print("🚀 Initializing Web Automation Shell...", style="bold blue")
            
            # Initialize web automator
            self.automator = WebAutomator(self.config)
            
            # Initialize Claude client
            try:
                self.claude = ClaudeClient()
                console.print("✅ Claude Sonnet 4.5 connected", style="green")
            except Exception as e:
                console.print(f"⚠️ Claude not available: {e}", style="yellow")
            
            console.print("✅ Web Automation Shell ready!", style="green")
            
        except Exception as e:
            console.print(f"❌ Initialization failed: {e}", style="red")
    
    def log_action(self, action: str, success: bool):
        """Log an action"""
        self.actions_performed += 1
        if success:
            self.successful_actions += 1
    
    def get_success_rate(self) -> float:
        """Get success rate percentage"""
        if self.actions_performed == 0:
            return 0.0
        return (self.successful_actions / self.actions_performed) * 100
    
    # Navigation Commands
    def do_navigate(self, arg):
        """Navigate to a URL: navigate <url>"""
        if not arg:
            console.print("❌ Usage: navigate <url>", style="red")
            return
        
        console.print(f"🌐 Navigating to: {arg}")
        success = self.automator.navigate_to(arg)
        
        if success:
            console.print(f"✅ Successfully navigated to {arg}", style="green")
            # Get page info
            if self.automator.driver:
                title = self.automator.driver.title
                console.print(f"📄 Page title: {title}", style="dim")
        else:
            console.print(f"❌ Failed to navigate to {arg}", style="red")
        
        self.log_action(f"navigate {arg}", success)
    
    def do_search(self, arg):
        """Search on DuckDuckGo: search <query>"""
        if not arg:
            console.print("❌ Usage: search <query>", style="red")
            return
        
        console.print(f"🔍 Searching for: {arg}")
        
        # Navigate to DuckDuckGo
        navigate_success = self.automator.navigate_to("https://duckduckgo.com")
        if not navigate_success:
            console.print("❌ Failed to reach DuckDuckGo", style="red")
            self.log_action(f"search {arg}", False)
            return
        
        # Wait a moment for page to load
        time.sleep(2)
        
        # Find search box and type
        try:
            search_element = self.automator.find_element("input[name='q']")
            if search_element:
                search_element.clear()
                search_element.send_keys(arg)
                
                # Press Enter
                from selenium.webdriver.common.keys import Keys
                search_element.send_keys(Keys.RETURN)
                
                console.print(f"✅ Search completed for: {arg}", style="green")
                time.sleep(3)  # Wait for results
                
                # Get results info
                if self.automator.driver:
                    current_url = self.automator.driver.current_url
                    console.print(f"📄 Results URL: {current_url}", style="dim")
                
                self.log_action(f"search {arg}", True)
            else:
                console.print("❌ Search box not found", style="red")
                self.log_action(f"search {arg}", False)
                
        except Exception as e:
            console.print(f"❌ Search failed: {e}", style="red")
            self.log_action(f"search {arg}", False)
    
    def do_click(self, arg):
        """Click an element: click <selector>"""
        if not arg:
            console.print("❌ Usage: click <selector>", style="red")
            return
        
        console.print(f"👆 Clicking: {arg}")
        success = self.automator.click_element(arg)
        
        if success:
            console.print(f"✅ Clicked: {arg}", style="green")
        else:
            console.print(f"❌ Failed to click: {arg}", style="red")
        
        self.log_action(f"click {arg}", success)
    
    def do_type(self, arg):
        """Type text in element: type <selector> <text>"""
        parts = arg.split(' ', 1)
        if len(parts) < 2:
            console.print("❌ Usage: type <selector> <text>", style="red")
            return
        
        selector, text = parts
        console.print(f"⌨️ Typing '{text}' in: {selector}")
        success = self.automator.type_in_element(selector, text)
        
        if success:
            console.print(f"✅ Text entered in: {selector}", style="green")
        else:
            console.print(f"❌ Failed to type in: {selector}", style="red")
        
        self.log_action(f"type {selector}", success)
    
    def do_find(self, arg):
        """Find element on page: find <selector>"""
        if not arg:
            console.print("❌ Usage: find <selector>", style="red")
            return
        
        console.print(f"🔍 Looking for: {arg}")
        element = self.automator.find_element(arg)
        
        if element:
            console.print(f"✅ Element found: {arg}", style="green")
            # Try to get element info
            try:
                tag_name = element.tag_name
                text = element.text[:50] + "..." if len(element.text) > 50 else element.text
                console.print(f"📄 Tag: {tag_name}, Text: '{text}'", style="dim")
            except:
                pass
        else:
            console.print(f"❌ Element not found: {arg}", style="red")
        
        self.log_action(f"find {arg}", element is not None)
    
    def do_screenshot(self, arg):
        """Take a screenshot: screenshot [filename]"""
        filename = arg if arg else "user_screenshot"
        console.print("📸 Taking screenshot...")
        
        try:
            screenshot_path = self.automator.take_screenshot()
            if screenshot_path:
                console.print(f"✅ Screenshot saved: {screenshot_path}", style="green")
                success = True
            else:
                console.print("❌ Failed to take screenshot", style="red")
                success = False
        except Exception as e:
            console.print(f"❌ Screenshot failed: {e}", style="red")
            success = False
        
        self.log_action("screenshot", success)
    
    def do_analyze(self, arg):
        """Analyze current page: analyze"""
        console.print("🔍 Analyzing current page...")
        
        if not self.automator.driver:
            console.print("❌ No active browser session", style="red")
            return
        
        try:
            driver = self.automator.driver
            
            # Get basic page info
            title = driver.title
            url = driver.current_url
            
            # Count elements
            links = len(driver.find_elements('tag name', 'a'))
            buttons = len(driver.find_elements('tag name', 'button'))
            inputs = len(driver.find_elements('tag name', 'input'))
            forms = len(driver.find_elements('tag name', 'form'))
            headings = len(driver.find_elements('css selector', 'h1,h2,h3,h4,h5,h6'))
            images = len(driver.find_elements('tag name', 'img'))
            
            # Create analysis table
            table = Table(title="📋 Page Analysis Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")
            
            table.add_row("📄 Title", title[:80] + "..." if len(title) > 80 else title)
            table.add_row("🌐 URL", url)
            table.add_row("🔗 Links", str(links))
            table.add_row("🔲 Buttons", str(buttons))
            table.add_row("📝 Input Fields", str(inputs))
            table.add_row("📋 Forms", str(forms))
            table.add_row("📰 Headings", str(headings))
            table.add_row("🖼️ Images", str(images))
            
            console.print(table)
            self.log_action("analyze", True)
            
        except Exception as e:
            console.print(f"❌ Analysis failed: {e}", style="red")
            self.log_action("analyze", False)
    
    def do_demo(self, arg):
        """Run demonstration examples: demo"""
        console.print("🎭 Running demonstration examples...", style="bold blue")
        
        demos = [
            ("navigate https://example.com", "Navigate to Example.com"),
            ("analyze", "Analyze the page"),
            ("search Python automation", "Search for Python automation"),
            ("screenshot", "Take a screenshot")
        ]
        
        for command, description in demos:
            console.print(f"\n🔹 {description}", style="bold cyan")
            console.print(f"   Command: {command}", style="dim")
            
            # Execute the command
            self.onecmd(command)
            
            # Brief pause between demos
            time.sleep(2)
        
        console.print("\n✅ Demo completed!", style="green")
    
    def do_status(self, arg):
        """Show service status: status"""
        runtime = datetime.now() - self.session_start
        
        table = Table(title="🌐 Web Automation Service Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("🕐 Runtime", str(runtime).split('.')[0])
        table.add_row("📊 Total Actions", str(self.actions_performed))
        table.add_row("✅ Successful Actions", str(self.successful_actions))
        table.add_row("📈 Success Rate", f"{self.get_success_rate():.1f}%")
        table.add_row("🌐 Browser", self.config.get('browser', 'unknown'))
        table.add_row("🤖 Claude Status", "✅ Connected" if self.claude else "❌ Not available")
        
        console.print(table)
    
    def do_help(self, arg):
        """Show available commands"""
        if arg:
            # Show help for specific command
            super().do_help(arg)
        else:
            # Show all commands with descriptions
            console.print("📋 Available Commands:", style="bold blue")
            
            commands = [
                ("navigate <url>", "Navigate to a website"),
                ("search <query>", "Search on DuckDuckGo"),
                ("click <selector>", "Click an element"),
                ("type <selector> <text>", "Type text in an element"),
                ("find <selector>", "Find element on page"),
                ("screenshot", "Take a screenshot"),
                ("analyze", "Analyze current page elements"),
                ("demo", "Run demonstration examples"),
                ("status", "Show service status"),
                ("quit", "Exit the shell"),
                ("help", "Show this help message")
            ]
            
            for cmd_name, description in commands:
                console.print(f"  {cmd_name:<25} - {description}")
    
    def do_quit(self, arg):
        """Exit the shell: quit"""
        console.print("👋 Shutting down Web Automation Shell...")
        
        if self.automator:
            try:
                self.automator.cleanup()
            except:
                pass
        
        console.print("✅ Goodbye!", style="green")
        return True
    
    # Aliases
    do_exit = do_quit
    do_q = do_quit
    
    def emptyline(self):
        """Handle empty line input"""
        pass
    
    def default(self, line):
        """Handle unknown commands"""
        console.print(f"❌ Unknown command: {line}. Type 'help' for available commands.", style="red")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Persistent Web Automation Shell")
    parser.add_argument("--demo", action="store_true", help="Run demo and exit")
    
    args = parser.parse_args()
    
    # Create and start shell
    shell = WebAutomationShell()
    
    if args.demo:
        # Run demo mode
        shell.onecmd("demo")
        shell.onecmd("quit")
    else:
        # Start interactive shell
        try:
            shell.cmdloop()
        except KeyboardInterrupt:
            console.print("\n\n👋 Goodbye!")
            shell.onecmd("quit")


if __name__ == "__main__":
    main()