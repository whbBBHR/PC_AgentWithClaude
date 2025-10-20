#!/usr/bin/env python3
"""
Manual Interactive Web Automation Shell
A truly interactive shell that accepts real user input for web automation commands
Powered by Claude Sonnet 4.5 for intelligent automation guidance.
"""

import os
import sys
import json
import time
import readline  # Enable command history and editing
from typing import Optional, Dict, Any, List
from datetime import datetime

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import our automation components
from src.pc_agent.web_automator import WebAutomator
from src.pc_agent.claude_client import ClaudeClient

# Load environment
load_dotenv()

console = Console()


class ManualWebAutomationShell:
    """Interactive shell with manual user input for web automation commands"""
    
    def __init__(self):
        self.config = self.load_config()
        self.automator = None
        self.claude = None
        self.session_start = datetime.now()
        self.actions_performed = 0
        self.successful_actions = 0
        self.running = True
        
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
            console.print("🚀 Initializing Manual Web Automation Shell...", style="bold blue")
            
            # Initialize web automator
            self.automator = WebAutomator(self.config)
            
            # Initialize Claude client
            try:
                self.claude = ClaudeClient()
                console.print("✅ Claude Sonnet 4.5 connected", style="green")
            except Exception as e:
                console.print(f"⚠️ Claude not available: {e}", style="yellow")
            
            console.print("✅ Manual Web Automation Shell ready!", style="green")
            
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
    
    def show_help(self):
        """Show available commands"""
        console.print("\n📋 Available Commands:", style="bold blue")
        
        commands = [
            ("navigate <url>", "Navigate to a website", "navigate https://example.com"),
            ("search <query>", "Search on DuckDuckGo", "search Python automation"),
            ("click <selector>", "Click an element", "click button.submit"),
            ("type <selector> <text>", "Type text in an element", "type input#email hello@example.com"),
            ("find <selector>", "Find element on page", "find input[name='q']"),
            ("screenshot", "Take a screenshot", "screenshot"),
            ("analyze", "Analyze current page elements", "analyze"),
            ("demo", "Run demonstration examples", "demo"),
            ("status", "Show service status", "status"),
            ("help", "Show this help message", "help"),
            ("quit", "Exit the shell", "quit")
        ]
        
        table = Table(title="Command Reference")
        table.add_column("Command", style="cyan", width=25)
        table.add_column("Description", style="white", width=30)
        table.add_column("Example", style="dim", width=30)
        
        for cmd, desc, example in commands:
            table.add_row(cmd, desc, example)
        
        console.print(table)
    
    def show_status(self):
        """Show service status"""
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
    
    def navigate_to_url(self, url: str) -> bool:
        """Navigate to a URL"""
        console.print(f"🌐 Navigating to: {url}")
        success = self.automator.navigate_to(url)
        
        if success:
            console.print(f"✅ Successfully navigated to {url}", style="green")
            # Get page info
            if self.automator.driver:
                title = self.automator.driver.title
                console.print(f"📄 Page title: {title}", style="dim")
        else:
            console.print(f"❌ Failed to navigate to {url}", style="red")
        
        self.log_action(f"navigate {url}", success)
        return success
    
    def search_duckduckgo(self, query: str) -> bool:
        """Search on DuckDuckGo"""
        console.print(f"🔍 Searching for: {query}")
        
        # Navigate to DuckDuckGo
        navigate_success = self.automator.navigate_to("https://duckduckgo.com")
        if not navigate_success:
            console.print("❌ Failed to reach DuckDuckGo", style="red")
            self.log_action(f"search {query}", False)
            return False
        
        # Wait a moment for page to load
        time.sleep(2)
        
        # Find search box and type
        try:
            search_element = self.automator.find_element("input[name='q']")
            if search_element:
                search_element.clear()
                search_element.send_keys(query)
                
                # Press Enter
                from selenium.webdriver.common.keys import Keys
                search_element.send_keys(Keys.RETURN)
                
                console.print(f"✅ Search completed for: {query}", style="green")
                time.sleep(3)  # Wait for results
                
                # Get results info
                if self.automator.driver:
                    current_url = self.automator.driver.current_url
                    console.print(f"📄 Results URL: {current_url}", style="dim")
                
                self.log_action(f"search {query}", True)
                return True
            else:
                console.print("❌ Search box not found", style="red")
                self.log_action(f"search {query}", False)
                return False
                
        except Exception as e:
            console.print(f"❌ Search failed: {e}", style="red")
            self.log_action(f"search {query}", False)
            return False
    
    def analyze_page(self) -> bool:
        """Analyze current page"""
        console.print("🔍 Analyzing current page...")
        
        if not self.automator.driver:
            console.print("❌ No active browser session", style="red")
            return False
        
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
            return True
            
        except Exception as e:
            console.print(f"❌ Analysis failed: {e}", style="red")
            self.log_action("analyze", False)
            return False
    
    def run_demo(self):
        """Run demonstration examples"""
        console.print("🎭 Running demonstration examples...", style="bold blue")
        
        demos = [
            ("Navigate to Example.com", lambda: self.navigate_to_url("https://example.com")),
            ("Analyze the page", lambda: self.analyze_page()),
            ("Search for Python automation", lambda: self.search_duckduckgo("Python automation")),
        ]
        
        for description, demo_func in demos:
            console.print(f"\n🔹 {description}", style="bold cyan")
            demo_func()
            
            # Brief pause between demos
            time.sleep(2)
        
        console.print("\n✅ Demo completed!", style="green")
    
    def process_command(self, command_line: str):
        """Process a user command"""
        if not command_line.strip():
            return
        
        parts = command_line.strip().split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        try:
            if cmd == "help":
                self.show_help()
            
            elif cmd == "status":
                self.show_status()
            
            elif cmd == "navigate":
                if args:
                    self.navigate_to_url(args[0])
                else:
                    console.print("❌ Usage: navigate <url>", style="red")
            
            elif cmd == "search":
                if args:
                    query = " ".join(args)
                    self.search_duckduckgo(query)
                else:
                    console.print("❌ Usage: search <query>", style="red")
            
            elif cmd == "analyze":
                self.analyze_page()
            
            elif cmd == "demo":
                self.run_demo()
            
            elif cmd == "find":
                if args:
                    selector = " ".join(args)
                    console.print(f"🔍 Looking for: {selector}")
                    element = self.automator.find_element(selector)
                    if element:
                        console.print(f"✅ Element found: {selector}", style="green")
                        try:
                            tag_name = element.tag_name
                            text = element.text[:50] + "..." if len(element.text) > 50 else element.text
                            console.print(f"📄 Tag: {tag_name}, Text: '{text}'", style="dim")
                        except:
                            pass
                    else:
                        console.print(f"❌ Element not found: {selector}", style="red")
                    self.log_action(f"find {selector}", element is not None)
                else:
                    console.print("❌ Usage: find <selector>", style="red")
            
            elif cmd == "click":
                if args:
                    selector = " ".join(args)
                    console.print(f"👆 Clicking: {selector}")
                    success = self.automator.click_element(selector)
                    if success:
                        console.print(f"✅ Clicked: {selector}", style="green")
                    else:
                        console.print(f"❌ Failed to click: {selector}", style="red")
                    self.log_action(f"click {selector}", success)
                else:
                    console.print("❌ Usage: click <selector>", style="red")
            
            elif cmd == "type":
                if len(args) >= 2:
                    selector = args[0]
                    text = " ".join(args[1:])
                    console.print(f"⌨️ Typing '{text}' in: {selector}")
                    success = self.automator.type_in_element(selector, text)
                    if success:
                        console.print(f"✅ Text entered in: {selector}", style="green")
                    else:
                        console.print(f"❌ Failed to type in: {selector}", style="red")
                    self.log_action(f"type {selector}", success)
                else:
                    console.print("❌ Usage: type <selector> <text>", style="red")
            
            elif cmd == "screenshot":
                console.print("📸 Taking screenshot...")
                try:
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    screenshot_path = self.automator.take_screenshot(f"user_screenshot_{timestamp}")
                    console.print(f"✅ Screenshot saved: {screenshot_path}", style="green")
                    self.log_action("screenshot", True)
                except Exception as e:
                    console.print(f"❌ Screenshot failed: {e}", style="red")
                    self.log_action("screenshot", False)
            
            elif cmd in ["quit", "exit", "q"]:
                self.running = False
                console.print("👋 Shutting down Web Automation Shell...")
                if self.automator:
                    try:
                        self.automator.cleanup()
                    except:
                        pass
                console.print("✅ Goodbye!", style="green")
            
            else:
                console.print(f"❌ Unknown command: {cmd}. Type 'help' for available commands.", style="red")
        
        except Exception as e:
            console.print(f"❌ Command failed: {e}", style="red")
    
    def run(self):
        """Run the interactive shell"""
        console.clear()
        
        # Show welcome message
        welcome_panel = Panel.fit(
            "🌐 Manual Web Automation Shell - Claude Sonnet 4.5\n\n" +
            "A truly interactive service for web automation.\n" +
            "Type 'help' for available commands or 'demo' for examples.\n\n" +
            "✅ Ready for your commands!",
            style="bold blue"
        )
        console.print(welcome_panel)
        
        # Show initial help
        self.show_help()
        
        console.print("\n💡 Type commands below. Use 'quit' to exit.\n", style="yellow")
        
        # Main command loop
        while self.running:
            try:
                # Get user input manually
                command = input("🤖 web-automation> ")
                
                # Process the command
                self.process_command(command)
                
            except KeyboardInterrupt:
                console.print("\n\n👋 Interrupted by user!")
                self.running = False
                if self.automator:
                    try:
                        self.automator.cleanup()
                    except:
                        pass
                console.print("✅ Goodbye!", style="green")
                break
            except EOFError:
                console.print("\n👋 End of input!")
                self.running = False
                break


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manual Interactive Web Automation Shell")
    parser.add_argument("--demo", action="store_true", help="Run demo and exit")
    
    args = parser.parse_args()
    
    # Create and start shell
    shell = ManualWebAutomationShell()
    
    if args.demo:
        # Run demo mode
        shell.run_demo()
        console.print("👋 Demo completed!")
    else:
        # Start interactive shell
        shell.run()


if __name__ == "__main__":
    main()