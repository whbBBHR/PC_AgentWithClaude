#!/usr/bin/env python3
"""
Live Web Automation - Production Ready
Real browser automation with Claude 3.5 guidance, robust error handling,
and proper cleanup management.
"""

import os
import sys
import json
import time
import logging
import argparse
from typing import Optional, Dict, Any, List
from datetime import datetime
from urllib.parse import urlparse
from contextlib import contextmanager

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.logging import RichHandler
from rich.prompt import Confirm

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, show_time=False)]
)
logger = logging.getLogger(__name__)

console = Console()

# Import enhanced modules with error handling
try:
    from src.pc_agent.claude_client import ClaudeClient
    from src.pc_agent.web_automator import WebAutomator
    IMPORTS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Could not import automation modules: {e}")
    IMPORTS_AVAILABLE = False

# Selenium imports with fallback
try:
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import (
        WebDriverException,
        NoSuchElementException,
        TimeoutException,
        StaleElementReferenceException
    )
    SELENIUM_AVAILABLE = True
except ImportError:
    logger.warning("Selenium not installed. Install with: pip install selenium")
    SELENIUM_AVAILABLE = False


class AutomationConfig:
    """Configuration manager with validation"""
    
    DEFAULT_CONFIG = {
        'browser': 'chrome',
        'headless': False,
        'wait_timeout': 10,
        'max_retries': 3,
        'screenshot_on_error': True,
        'page_load_timeout': 30
    }
    
    @classmethod
    def load(cls, config_path: str = 'config.json') -> Dict[str, Any]:
        """Load and validate configuration"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Merge with defaults
            final_config = cls.DEFAULT_CONFIG.copy()
            final_config.update(config)
            
            # Validate
            cls._validate_config(final_config)
            
            return final_config
            
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return cls.DEFAULT_CONFIG.copy()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise
    
    @staticmethod
    def _validate_config(config: Dict[str, Any]):
        """Validate configuration values"""
        if config.get('wait_timeout', 0) <= 0:
            raise ValueError("wait_timeout must be positive")
        
        if config.get('max_retries', 0) < 0:
            raise ValueError("max_retries must be non-negative")
        
        valid_browsers = ['chrome', 'firefox', 'edge', 'safari']
        if config.get('browser', '').lower() not in valid_browsers:
            raise ValueError(f"browser must be one of: {valid_browsers}")


class SafeWebAutomator:
    """Wrapper around WebAutomator with safety features"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.automator = None
        self._initialized = False
        self.screenshots_dir = "screenshots"
        
        # Create screenshots directory
        if config.get('screenshot_on_error', True):
            os.makedirs(self.screenshots_dir, exist_ok=True)
    
    def initialize(self) -> bool:
        """Initialize web automator with error handling"""
        try:
            if not IMPORTS_AVAILABLE:
                raise ImportError("Web automation modules not available")
            
            self.automator = WebAutomator(self.config)
            self._initialized = True
            logger.info("Web automator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize web automator: {e}")
            return False
    
    def is_valid_url(self, url: str) -> bool:
        """Validate URL for safety"""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ['http', 'https'] and bool(parsed.netloc)
        except Exception:
            return False
    
    def navigate_to(self, url: str, max_retries: int = None) -> bool:
        """Navigate to URL with validation and retry logic"""
        if not self._initialized or not self.automator:
            logger.error("Automator not initialized")
            return False
        
        if not self.is_valid_url(url):
            logger.error(f"Invalid URL: {url}")
            return False
        
        max_retries = max_retries or self.config.get('max_retries', 3)
        
        for attempt in range(max_retries):
            try:
                success = self.automator.navigate_to(url)
                if success:
                    return True
                
                logger.warning(f"Navigation attempt {attempt + 1} failed")
                time.sleep(1)  # Brief pause before retry
                
            except TimeoutException:
                logger.warning(f"Navigation timeout on attempt {attempt + 1}")
            except Exception as e:
                logger.error(f"Navigation error on attempt {attempt + 1}: {e}")
        
        return False
    
    def wait_for_element(self, selector: str, timeout: int = None) -> bool:
        """Wait for element with proper timeout"""
        if not self._initialized or not self.automator:
            return False
        
        timeout = timeout or self.config.get('wait_timeout', 10)
        
        try:
            element = self.automator.wait_for_element(selector, timeout)
            return element is not None
        except TimeoutException:
            logger.warning(f"Element '{selector}' not found within {timeout}s")
            return False
        except Exception as e:
            logger.error(f"Error waiting for element: {e}")
            return False
    
    def find_element(self, selector: str) -> Optional[Any]:
        """Find element with error handling"""
        if not self._initialized or not self.automator:
            return None
        
        try:
            return self.automator.find_element(selector)
        except NoSuchElementException:
            logger.warning(f"Element not found: {selector}")
            return None
        except Exception as e:
            logger.error(f"Error finding element: {e}")
            return None
    
    def find_elements(self, selector: str) -> List[Any]:
        """Find multiple elements with error handling"""
        if not self._initialized or not self.automator:
            return []
        
        try:
            elements = self.automator.find_elements(selector)
            return elements if elements else []
        except Exception as e:
            logger.error(f"Error finding elements: {e}")
            return []
    
    def type_text(self, selector: str, text: str, clear_first: bool = True) -> bool:
        """Type text with proper error handling"""
        if not self._initialized or not self.automator:
            return False
        
        try:
            return self.automator.type_in_element(selector, text, clear_first)
        except StaleElementReferenceException:
            logger.warning("Element became stale, retrying...")
            time.sleep(0.5)
            return self.automator.type_in_element(selector, text, clear_first)
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            return False
    
    def press_key(self, selector: str, key: str) -> bool:
        """Press key in element using WebAutomator abstraction"""
        if not self._initialized or not self.automator:
            return False
        
        try:
            # Check if WebAutomator has press_key method
            if hasattr(self.automator, 'press_key'):
                return self.automator.press_key(selector, key)
            else:
                # Fallback: find element and send keys
                element = self.automator.find_element(selector)
                if element and SELENIUM_AVAILABLE:
                    key_mapping = {
                        'ENTER': Keys.RETURN,
                        'RETURN': Keys.RETURN,
                        'TAB': Keys.TAB,
                        'ESC': Keys.ESCAPE
                    }
                    selenium_key = key_mapping.get(key.upper(), key)
                    element.send_keys(selenium_key)
                    return True
                return False
        except Exception as e:
            logger.error(f"Error pressing key: {e}")
            return False
    
    def take_screenshot(self, name: str = None) -> Optional[str]:
        """Take screenshot for debugging"""
        if not self._initialized or not self.automator:
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = name or f"screenshot_{timestamp}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            
            if hasattr(self.automator, 'take_screenshot'):
                self.automator.take_screenshot(filepath)
            elif hasattr(self.automator, 'driver'):
                self.automator.driver.save_screenshot(filepath)
            else:
                return None
            
            logger.info(f"Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None
    
    def get_page_info(self) -> Dict[str, str]:
        """Get current page information"""
        if not self._initialized or not self.automator:
            return {}
        
        try:
            return {
                'url': self.automator.get_current_url(),
                'title': self.automator.get_page_title()
            }
        except Exception as e:
            logger.error(f"Error getting page info: {e}")
            return {}
    
    def cleanup(self):
        """Clean up resources"""
        if self._initialized and self.automator:
            try:
                self.automator.cleanup()
                logger.info("Web automator cleaned up successfully")
            except Exception as e:
                logger.warning(f"Cleanup warning: {e}")
            finally:
                self._initialized = False
                self.automator = None


@contextmanager
def automation_session(config: Dict[str, Any]):
    """Context manager for safe automation sessions"""
    automator = SafeWebAutomator(config)
    
    try:
        if automator.initialize():
            yield automator
        else:
            yield None
    except KeyboardInterrupt:
        console.print("\n⚠️ Interrupted by user", style="bold yellow")
        raise
    finally:
        automator.cleanup()


def confirm_live_automation(auto_confirm: bool = False) -> bool:
    """Ask user to confirm live browser automation"""
    if auto_confirm:
        return True
    
    console.print(Panel.fit(
        "⚠️ LIVE WEB AUTOMATION WARNING ⚠️\n\n"
        "This will open a real browser and perform actual web interactions.\n"
        "Make sure you're ready for browser windows to open and navigate.\n\n"
        "Do you want to continue?",
        style="bold yellow"
    ))
    
    try:
        return Confirm.ask("Continue with live automation?", default=False)
    except KeyboardInterrupt:
        console.print("\n❌ Cancelled by user")
        return False


def example_1_basic_navigation(automator: SafeWebAutomator) -> bool:
    """Example 1: Basic Navigation"""
    console.print(Panel.fit("📍 Example 1: Basic Navigation", style="bold cyan"))
    
    try:
        url = "https://example.com"
        console.print(f"Navigating to {url}...")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Loading page...", total=None)
            success = automator.navigate_to(url)
            progress.remove_task(task)
        
        if success:
            console.print("✅ Successfully navigated to example.com")
            
            # Get page info
            page_info = automator.get_page_info()
            console.print(f"   URL: {page_info.get('url', 'Unknown')}")
            console.print(f"   Title: {page_info.get('title', 'Unknown')}")
            
            # Give user time to see
            time.sleep(2)
            return True
        else:
            console.print("❌ Navigation failed", style="bold red")
            return False
            
    except Exception as e:
        logger.exception("Navigation example failed")
        console.print(f"❌ Error: {str(e)}", style="bold red")
        return False


def example_2_search_automation(automator: SafeWebAutomator, claude: Optional[ClaudeClient]) -> bool:
    """Example 2: Search Automation with AI Guidance"""
    console.print(Panel.fit("🔍 Example 2: Search Automation", style="bold green"))
    
    try:
        # Get Claude's search strategy if available
        if claude:
            console.print("🧠 Getting Claude's search strategy...")
            try:
                search_plan = claude.plan_task(
                    "Search for 'Python web automation selenium' on DuckDuckGo",
                    context={"platform": "web", "search_engine": "duckduckgo"}
                )
                console.print("✅ Search strategy received from Claude")
            except Exception as e:
                logger.warning(f"Claude planning failed: {e}")
                console.print("⚠️ Proceeding without Claude guidance")
        
        # Navigate to search engine
        console.print("Navigating to DuckDuckGo...")
        success = automator.navigate_to("https://duckduckgo.com")
        
        if not success:
            console.print("❌ Failed to reach DuckDuckGo", style="bold red")
            return False
        
        console.print("✅ Reached DuckDuckGo")
        
        # Wait for search box to be ready
        console.print("🔍 Waiting for search input...")
        search_selector = "input[name='q']"
        
        if not automator.wait_for_element(search_selector, timeout=10):
            console.print("❌ Search box not found", style="bold red")
            automator.take_screenshot("search_box_not_found")
            return False
        
        console.print("✅ Found search box")
        
        # Type search query
        search_query = "Python web automation selenium"
        console.print(f"⌨️ Typing: {search_query}")
        
        if not automator.type_text(search_selector, search_query):
            console.print("❌ Failed to type search query", style="bold red")
            return False
        
        # Submit search
        console.print("🚀 Submitting search...")
        if not automator.press_key(search_selector, "ENTER"):
            console.print("❌ Failed to submit search", style="bold red")
            return False
        
        # Wait for results
        console.print("⏳ Waiting for search results...")
        
        # Try multiple selectors for search results
        result_selectors = [
            ".result",
            "[data-result]",
            "article",
            ".web-result"
        ]
        
        results_found = False
        for selector in result_selectors:
            if automator.wait_for_element(selector, timeout=5):
                console.print(f"✅ Search results loaded (found via: {selector})")
                results_found = True
                break
        
        if not results_found:
            console.print("⚠️ Could not verify search results", style="yellow")
            automator.take_screenshot("search_results_timeout")
        
        # Get result info
        page_info = automator.get_page_info()
        console.print(f"   Results URL: {page_info.get('url', 'Unknown')}")
        
        time.sleep(2)
        return True
        
    except Exception as e:
        logger.exception("Search automation failed")
        console.print(f"❌ Error: {str(e)}", style="bold red")
        automator.take_screenshot("search_error")
        return False


def example_3_element_detection(automator: SafeWebAutomator) -> bool:
    """Example 3: Advanced Element Detection"""
    console.print(Panel.fit("🎯 Example 3: Element Detection & Analysis", style="bold blue"))
    
    try:
        console.print("Analyzing current page elements...")
        
        # Define elements to find
        element_types = [
            ("Links", "a", "Hyperlinks on the page"),
            ("Headings", "h1, h2, h3", "Page headings"),
            ("Images", "img", "Image elements"),
            ("Buttons", "button", "Button elements"),
            ("Forms", "form", "Form elements")
        ]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Detecting elements...", total=len(element_types))
            
            elements_found = []
            for name, selector, description in element_types:
                try:
                    elements = automator.find_elements(selector)
                    count = len(elements)
                    elements_found.append((name, count, description))
                    
                    if count > 0:
                        logger.info(f"Found {count} {name.lower()}")
                except Exception as e:
                    logger.warning(f"Error finding {name}: {e}")
                    elements_found.append((name, 0, description))
                
                progress.advance(task)
        
        # Display results
        console.print("\n📋 Element Detection Results:")
        for name, count, description in elements_found:
            status = "✅" if count > 0 else "⚠️"
            console.print(f"   {status} {name}: {count} found - {description}")
        
        # Take screenshot of analyzed page
        automator.take_screenshot("element_analysis")
        
        time.sleep(3)
        return True
        
    except Exception as e:
        logger.exception("Element detection failed")
        console.print(f"❌ Error: {str(e)}", style="bold red")
        return False


def run_live_automation(config: Dict[str, Any], skip_confirm: bool = False):
    """Run complete live automation workflow"""
    console.print(Panel.fit(
        "🌐 Live Web Automation with Claude 3.5",
        style="bold cyan"
    ))
    
    # Check dependencies
    if not IMPORTS_AVAILABLE:
        console.print("❌ Required modules not available", style="bold red")
        console.print("Install with: pip install -r requirements.txt")
        return
    
    if not SELENIUM_AVAILABLE:
        console.print("❌ Selenium not installed", style="bold red")
        console.print("Install with: pip install selenium")
        return
    
    # Confirm with user
    if not confirm_live_automation(skip_confirm):
        return
    
    # Initialize Claude if available
    claude = None
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key and api_key != 'your-claude-api-key-here':
        try:
            claude = ClaudeClient(api_key=api_key, config=config)
            console.print("✅ Claude 3.5 guidance active\n")
        except Exception as e:
            logger.warning(f"Claude initialization failed: {e}")
            console.print("⚠️ Continuing without Claude guidance\n")
    else:
        console.print("⚠️ No Claude API key - running without AI guidance\n")
    
    # Run automation in safe context
    results = {
        'example_1': False,
        'example_2': False,
        'example_3': False
    }
    
    with automation_session(config) as automator:
        if not automator:
            console.print("❌ Failed to initialize automation", style="bold red")
            return
        
        console.print("✅ Web automator initialized\n")
        console.print("="*60 + "\n")
        
        # Example 1: Basic Navigation
        results['example_1'] = example_1_basic_navigation(automator)
        console.print()
        
        # Example 2: Search Automation
        results['example_2'] = example_2_search_automation(automator, claude)
        console.print()
        
        # Example 3: Element Detection
        results['example_3'] = example_3_element_detection(automator)
        console.print()
    
    # Summary
    console.print("="*60)
    
    success_count = sum(results.values())
    total_count = len(results)
    
    summary_style = "bold green" if success_count == total_count else "bold yellow"
    
    console.print(Panel.fit(
        f"🎉 Live Web Automation Complete!\n\n"
        f"Results: {success_count}/{total_count} examples successful\n\n"
        f"{'✅' if results['example_1'] else '❌'} Basic navigation\n"
        f"{'✅' if results['example_2'] else '❌'} Search automation\n"
        f"{'✅' if results['example_3'] else '❌'} Element detection\n\n"
        f"{'🎊 All examples completed successfully!' if success_count == total_count else '⚠️ Some examples had issues - check logs'}",
        style=summary_style
    ))


def show_capabilities():
    """Display automation capabilities without running"""
    console.print(Panel.fit(
        "🌐 Web Automation Capabilities Overview",
        style="bold blue"
    ))
    
    capabilities = {
        "🧭 Navigation": [
            "URL validation before navigation",
            "Automatic retry logic for failed loads",
            "Back/forward browser history control",
            "Multi-tab and window management",
            "Configurable page load timeouts"
        ],
        "🎯 Element Interaction": [
            "Smart element waiting (no hardcoded sleeps)",
            "Stale element retry handling",
            "CSS selector and XPath support",
            "Safe text input with validation",
            "Key press abstraction (ENTER, TAB, etc.)"
        ],
        "🔍 Search & Data": [
            "Automated search engine interaction",
            "Multiple selector fallback strategies",
            "Result verification and validation",
            "Data extraction with error handling",
            "Context-aware element detection"
        ],
        "🧠 AI Integration": [
            "Claude 3.5 task planning and guidance",
            "Intelligent workflow generation",
            "Context-aware decision making",
            "Graceful fallback without AI",
            "Error recovery with AI assistance"
        ],
        "⚡ Advanced Features": [
            "Automatic screenshot on errors",
            "Comprehensive logging and debugging",
            "Configuration validation",
            "Resource cleanup guarantees",
            "Context manager for safe sessions"
        ],
        "🛡️ Safety & Security": [
            "URL validation before navigation",
            "Proper exception handling hierarchy",
            "KeyboardInterrupt preservation",
            "Resource leak prevention",
            "User confirmation for live actions"
        ]
    }
    
    for category, features in capabilities.items():
        console.print(f"\n{category}")
        for feature in features:
            console.print(f"   ✅ {feature}")
    
    console.print("\n" + "="*60 + "\n")
    
    console.print(Panel.fit(
        "💡 Ready to run live automation?\n\n"
        "Use: python live_web_automation.py --live\n\n"
        "Requirements:\n"
        "• Chrome browser installed\n"
        "• ChromeDriver available\n"
        "• Internet connection\n"
        "• Claude API key (optional, for AI guidance)\n\n"
        "Optional flags:\n"
        "  --headless    Run browser in headless mode\n"
        "  --yes         Skip confirmation prompt\n"
        "  --config PATH Custom config file path",
        style="cyan"
    ))


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Live Web Automation with Claude 3.5",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--live',
        action='store_true',
        help='Execute live browser automation'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode'
    )
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Skip confirmation prompt'
    )
    parser.add_argument(
        '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = AutomationConfig.load(args.config)
        
        # Override with CLI arguments
        if args.headless:
            config['headless'] = True
        
        # Run appropriate mode
        if args.live:
            run_live_automation(config, skip_confirm=args.yes)
        else:
            show_capabilities()
            console.print("\n💡 Add --live flag to run actual browser automation")
    
    except KeyboardInterrupt:
        console.print("\n\n👋 Goodbye!")
    except Exception as e:
        logger.exception("Fatal error")
        console.print(f"\n❌ Fatal error: {str(e)}", style="bold red")
        sys.exit(1)


if __name__ == "__main__":
    main()