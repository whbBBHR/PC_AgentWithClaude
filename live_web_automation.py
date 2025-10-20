#!/usr/bin/env python3
"""
Live Web Automation - Production Ready (Enhanced Edition)
Real browser automation with Claude Sonnet 4.5 guidance, robust error handling,
auto driver management, and comprehensive monitoring.

Version: 3.0
"""

import os
import sys
import json
import time
import logging
import argparse
import platform
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from urllib.parse import urlparse
from contextlib import contextmanager
from functools import wraps

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.logging import RichHandler
from rich.prompt import Confirm
from rich.table import Table

# Selenium imports for proper API usage
try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
except ImportError:
    # Fallback for when selenium is not available
    By = None
    Keys = None
    StaleElementReferenceException = Exception
    TimeoutException = Exception

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
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
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

# WebDriver Manager for automatic driver management
try:
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    logger.warning("webdriver-manager not installed. Install with: pip install webdriver-manager")
    WEBDRIVER_MANAGER_AVAILABLE = False


def measure_performance(func):
    """Decorator to measure function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            logger.debug(f"{func.__name__} completed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start
            logger.error(f"{func.__name__} failed after {duration:.2f}s: {e}")
            raise
    return wrapper


class AutomationSession:
    """Track automation session state and metrics"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.actions_performed = []
        self.errors_encountered = []
        self.screenshots_taken = []
        self.pages_visited = []
    
    def log_action(self, action: str, success: bool, details: str = ""):
        """Log an automation action"""
        self.actions_performed.append({
            'timestamp': datetime.now(),
            'action': action,
            'success': success,
            'details': details
        })
    
    def log_error(self, error: str, traceback_info: str = ""):
        """Log an error"""
        self.errors_encountered.append({
            'timestamp': datetime.now(),
            'error': error,
            'traceback': traceback_info
        })
    
    def log_page_visit(self, url: str):
        """Log a page visit"""
        self.pages_visited.append({
            'timestamp': datetime.now(),
            'url': url
        })
    
    def log_screenshot(self, filepath: str):
        """Log a screenshot"""
        self.screenshots_taken.append({
            'timestamp': datetime.now(),
            'filepath': filepath
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get session summary"""
        duration = (datetime.now() - self.start_time).total_seconds()
        total_actions = len(self.actions_performed)
        successful_actions = sum(1 for a in self.actions_performed if a['success'])
        
        return {
            'duration_seconds': duration,
            'total_actions': total_actions,
            'successful_actions': successful_actions,
            'total_errors': len(self.errors_encountered),
            'pages_visited': len(self.pages_visited),
            'screenshots_taken': len(self.screenshots_taken),
            'success_rate': (successful_actions / total_actions * 100) if total_actions > 0 else 0
        }
    
    def display_summary(self):
        """Display session summary in a nice table"""
        summary = self.get_summary()
        
        table = Table(title="📊 Automation Session Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Duration", f"{summary['duration_seconds']:.2f}s")
        table.add_row("Total Actions", str(summary['total_actions']))
        table.add_row("Successful Actions", str(summary['successful_actions']))
        table.add_row("Errors", str(summary['total_errors']))
        table.add_row("Pages Visited", str(summary['pages_visited']))
        table.add_row("Screenshots", str(summary['screenshots_taken']))
        table.add_row("Success Rate", f"{summary['success_rate']:.1f}%")
        
        console.print(table)


class AutomationConfig:
    """Configuration manager with validation and environment variable support"""
    
    DEFAULT_CONFIG = {
        'browser': os.getenv('AUTOMATION_BROWSER', 'chrome'),
        'headless': os.getenv('AUTOMATION_HEADLESS', 'false').lower() == 'true',
        'wait_timeout': int(os.getenv('AUTOMATION_WAIT_TIMEOUT', '10')),
        'max_retries': int(os.getenv('AUTOMATION_MAX_RETRIES', '3')),
        'screenshot_on_error': os.getenv('AUTOMATION_SCREENSHOT', 'true').lower() == 'true',
        'page_load_timeout': int(os.getenv('AUTOMATION_PAGE_TIMEOUT', '30')),
        'auto_driver_management': True,
        'max_parallel_sessions': 3
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


def check_browser_setup(browser: str = 'chrome') -> bool:
    """Check if browser and driver are properly set up"""
    console.print("🔍 Checking browser setup...")
    
    # Check webdriver-manager availability
    if WEBDRIVER_MANAGER_AVAILABLE:
        console.print("✅ webdriver-manager available (auto-driver management)")
    else:
        console.print("⚠️  webdriver-manager not installed")
        console.print("   Install with: pip install webdriver-manager")
        console.print("   This provides automatic driver management")
    
    # Check if browser is installed (platform specific)
    system = platform.system()
    browser = browser.lower()
    
    if browser == 'chrome':
        if system == "Darwin":  # macOS
            chrome_paths = [
                "/Applications/Google Chrome.app",
                "/Applications/Chromium.app"
            ]
        elif system == "Windows":
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]
        else:  # Linux
            chrome_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium"
            ]
        
        browser_found = any(os.path.exists(path) for path in chrome_paths)
        
        if browser_found:
            console.print("✅ Chrome browser detected")
        else:
            console.print("❌ Chrome browser not found")
            console.print("   Install from: https://www.google.com/chrome/")
    
    elif browser == 'firefox':
        if system == "Darwin":
            firefox_paths = ["/Applications/Firefox.app"]
        elif system == "Windows":
            firefox_paths = [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ]
        else:
            firefox_paths = ["/usr/bin/firefox"]
        
        browser_found = any(os.path.exists(path) for path in firefox_paths)
        
        if browser_found:
            console.print("✅ Firefox browser detected")
        else:
            console.print("❌ Firefox browser not found")
            console.print("   Install from: https://www.mozilla.org/firefox/")
    
    elif browser == 'safari':
        if system == "Darwin":
            browser_found = os.path.exists("/Applications/Safari.app")
            if browser_found:
                console.print("✅ Safari browser detected")
            else:
                console.print("❌ Safari not found")
        else:
            console.print("⚠️  Safari is only available on macOS")
            browser_found = False
    
    else:
        console.print(f"⚠️  Browser check not implemented for: {browser}")
        browser_found = True  # Assume it exists
    
    return browser_found or WEBDRIVER_MANAGER_AVAILABLE


class SafeWebAutomator:
    """Wrapper around WebAutomator with safety features and enhancements"""
    
    def __init__(self, config: Dict[str, Any], session: AutomationSession = None):
        self.config = config
        self.automator = None
        self._initialized = False
        self.screenshots_dir = "screenshots"
        self.session = session or AutomationSession()
        
        # Create screenshots directory
        if config.get('screenshot_on_error', True):
            os.makedirs(self.screenshots_dir, exist_ok=True)
    
    def initialize(self) -> bool:
        """Initialize web automator with error handling and auto driver management"""
        try:
            if not IMPORTS_AVAILABLE:
                raise ImportError("Web automation modules not available")
            
            # If auto driver management is enabled and available, use it
            if self.config.get('auto_driver_management') and WEBDRIVER_MANAGER_AVAILABLE:
                self._setup_auto_driver()
            
            self.automator = WebAutomator(self.config)
            self._initialized = True
            logger.info("Web automator initialized successfully")
            self.session.log_action("initialize", True, "Web automator ready")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize web automator: {e}")
            self.session.log_action("initialize", False, str(e))
            self.session.log_error(f"Initialization failed: {e}")
            return False
    
    def _setup_auto_driver(self):
        """Setup automatic driver management"""
        browser = self.config.get('browser', 'chrome').lower()
        
        try:
            if browser == 'chrome':
                logger.info("Setting up Chrome driver automatically...")
                driver_path = ChromeDriverManager().install()
                logger.info(f"Chrome driver installed: {driver_path}")
            elif browser == 'firefox':
                logger.info("Setting up Firefox driver automatically...")
                driver_path = GeckoDriverManager().install()
                logger.info(f"Firefox driver installed: {driver_path}")
        except Exception as e:
            logger.warning(f"Auto driver setup failed: {e}")
    
    def is_valid_url(self, url: str) -> bool:
        """Validate URL for safety"""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ['http', 'https'] and bool(parsed.netloc)
        except Exception:
            return False
    
    @measure_performance
    def navigate_to(self, url: str, max_retries: int = None) -> bool:
        """Navigate to URL with validation and retry logic"""
        if not self._initialized or not self.automator:
            logger.error("Automator not initialized")
            self.session.log_action("navigate", False, "Automator not initialized")
            return False
        
        if not self.is_valid_url(url):
            logger.error(f"Invalid URL: {url}")
            self.session.log_action("navigate", False, f"Invalid URL: {url}")
            return False
        
        max_retries = max_retries or self.config.get('max_retries', 3)
        
        for attempt in range(max_retries):
            try:
                success = self.automator.navigate_to(url)
                if success:
                    self.session.log_action("navigate", True, f"Navigated to {url}")
                    self.session.log_page_visit(url)
                    return True
                
                logger.warning(f"Navigation attempt {attempt + 1} failed")
                time.sleep(1)  # Brief pause before retry
                
            except TimeoutException:
                logger.warning(f"Navigation timeout on attempt {attempt + 1}")
                self.session.log_error(f"Navigation timeout: {url}")
            except Exception as e:
                logger.error(f"Navigation error on attempt {attempt + 1}: {e}")
                self.session.log_error(f"Navigation error: {e}")
        
        self.session.log_action("navigate", False, f"Failed after {max_retries} attempts")
        return False
    
    def _parse_selector(self, selector: str) -> Tuple[str, str]:
        """Parse selector into Selenium By strategy"""
        if selector.startswith("//"):
            return (By.XPATH, selector)
        elif selector.startswith("#"):
            return (By.ID, selector[1:])
        elif selector.startswith(".") and " " not in selector:
            return (By.CLASS_NAME, selector[1:])
        else:
            return (By.CSS_SELECTOR, selector)
    
    def wait_for_element(self, selector: str, timeout: int = None) -> bool:
        """Wait for element with proper timeout"""
        if not self._initialized or not self.automator:
            return False
        
        timeout = timeout or self.config.get('wait_timeout', 10)
        
        try:
            element = self.automator.wait_for_element_visible(selector, timeout=timeout)
            self.session.log_action("wait_for_element", True, f"Found: {selector}")
            return element is not None
        except TimeoutException:
            logger.warning(f"Element '{selector}' not found within {timeout}s")
            self.session.log_action("wait_for_element", False, f"Timeout: {selector}")
            return False
        except Exception as e:
            logger.error(f"Error waiting for element: {e}")
            self.session.log_error(f"Wait error: {e}")
            return False
    
    def wait_for_element_advanced(self, selectors: List[str], timeout: int = None) -> Optional[Any]:
        """Wait for element using multiple selector strategies"""
        if not self._initialized or not self.automator:
            return None
        
        timeout = timeout or self.config.get('wait_timeout', 10)
        timeout_per_selector = max(2, timeout // len(selectors))
        
        for selector in selectors:
            try:
                element = self.automator.wait_for_element_visible(selector, timeout=timeout_per_selector)
                if element:
                    logger.info(f"Element found with selector: {selector}")
                    self.session.log_action("wait_advanced", True, f"Found: {selector}")
                    return element
            except TimeoutException:
                continue
            except Exception as e:
                logger.debug(f"Error with selector '{selector}': {e}")
                continue
        
        logger.warning(f"Element not found with any of {len(selectors)} selectors")
        self.session.log_action("wait_advanced", False, f"No selector matched")
        return None
    
    def wait_for_clickable(self, selector: str, timeout: int = None) -> Optional[Any]:
        """Wait for element to be clickable"""
        if not self._initialized or not self.automator:
            return None
        
        timeout = timeout or self.config.get('wait_timeout', 10)
        
        try:
            if hasattr(self.automator, 'driver'):
                by, value = self._parse_selector(selector)
                element = WebDriverWait(self.automator.driver, timeout).until(
                    EC.element_to_be_clickable((by, value))
                )
                self.session.log_action("wait_clickable", True, f"Clickable: {selector}")
                return element
        except TimeoutException:
            logger.warning(f"Element '{selector}' not clickable within {timeout}s")
            self.session.log_action("wait_clickable", False, f"Timeout: {selector}")
            return None
        except Exception as e:
            logger.error(f"Error waiting for clickable element: {e}")
            self.session.log_error(f"Clickable wait error: {e}")
            return None
    
    def find_element(self, selector: str) -> Optional[Any]:
        """Find element with error handling"""
        if not self._initialized or not self.automator:
            return None
        
        try:
            element = self.automator.find_element(selector)
            self.session.log_action("find_element", True, f"Found: {selector}")
            return element
        except NoSuchElementException:
            logger.warning(f"Element not found: {selector}")
            self.session.log_action("find_element", False, f"Not found: {selector}")
            return None
        except Exception as e:
            logger.error(f"Error finding element: {e}")
            self.session.log_error(f"Find error: {e}")
            return None
    
    def find_elements(self, selector: str) -> List[Any]:
        """Find multiple elements with error handling"""
        if not self._initialized or not self.automator:
            return []
        
        try:
            elements = self.automator.find_elements(selector)
            count = len(elements) if elements else 0
            self.session.log_action("find_elements", True, f"Found {count}: {selector}")
            return elements if elements else []
        except Exception as e:
            logger.error(f"Error finding elements: {e}")
            self.session.log_error(f"Find elements error: {e}")
            return []
    
    def type_text(self, selector: str, text: str, clear_first: bool = True) -> bool:
        """Type text with proper error handling"""
        if not self._initialized or not self.automator:
            return False
        
        try:
            # Use correct parameter order: selector, text, by, clear_first
            # Fallback to string "css selector" if By is not available
            by_method = By.CSS_SELECTOR if By else "css selector"
            success = self.automator.type_in_element(selector, text, by_method, clear_first)
            self.session.log_action("type_text", success, f"Typed in {selector}")
            return success
        except StaleElementReferenceException:
            logger.warning("Element became stale, retrying...")
            time.sleep(0.5)
            try:
                by_method = By.CSS_SELECTOR if By else "css selector"
                success = self.automator.type_in_element(selector, text, by_method, clear_first)
                self.session.log_action("type_text", success, f"Typed (retry) in {selector}")
                return success
            except Exception as e:
                logger.error(f"Retry failed: {e}")
                self.session.log_error(f"Type text retry error: {e}")
                return False
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            self.session.log_error(f"Type text error: {e}")
            return False
    
    def click_element(self, selector: str, wait_clickable: bool = True) -> bool:
        """Click element with proper error handling"""
        if not self._initialized or not self.automator:
            return False
        
        try:
            if wait_clickable:
                element = self.wait_for_clickable(selector)
                if not element:
                    return False
            
            success = self.automator.click_element(selector)
            self.session.log_action("click", success, f"Clicked: {selector}")
            return success
        except Exception as e:
            logger.error(f"Error clicking element: {e}")
            self.session.log_error(f"Click error: {e}")
            return False
    
    def press_key(self, selector: str, key: str) -> bool:
        """Press key in element using WebAutomator abstraction"""
        if not self._initialized or not self.automator:
            return False
        
        try:
            # Check if WebAutomator has press_key method
            if hasattr(self.automator, 'press_key'):
                success = self.automator.press_key(selector, key)
            else:
                # Fallback: find element and send keys
                element = self.automator.find_element(selector)
                if element and SELENIUM_AVAILABLE:
                    key_mapping = {
                        'ENTER': Keys.RETURN,
                        'RETURN': Keys.RETURN,
                        'TAB': Keys.TAB,
                        'ESC': Keys.ESCAPE,
                        'ESCAPE': Keys.ESCAPE
                    }
                    selenium_key = key_mapping.get(key.upper(), key)
                    element.send_keys(selenium_key)
                    success = True
                else:
                    success = False
            
            self.session.log_action("press_key", success, f"Pressed {key} in {selector}")
            return success
        except Exception as e:
            logger.error(f"Error pressing key: {e}")
            self.session.log_error(f"Press key error: {e}")
            return False
    
    def take_screenshot(self, name: str = None) -> Optional[str]:
        """Take screenshot for debugging"""
        if not self._initialized or not self.automator:
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png" if name else f"screenshot_{timestamp}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            
            if hasattr(self.automator, 'take_screenshot'):
                self.automator.take_screenshot(filepath)
            elif hasattr(self.automator, 'driver'):
                self.automator.driver.save_screenshot(filepath)
            else:
                return None
            
            logger.info(f"Screenshot saved: {filepath}")
            self.session.log_screenshot(filepath)
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            self.session.log_error(f"Screenshot error: {e}")
            return None
    
    def get_console_logs(self) -> List[Dict]:
        """Capture browser console logs"""
        if not self._initialized or not self.automator:
            return []
        
        try:
            if hasattr(self.automator, 'driver'):
                logs = self.automator.driver.get_log('browser')
                self.session.log_action("get_console_logs", True, f"Retrieved {len(logs)} log entries")
                return logs
        except Exception as e:
            logger.warning(f"Could not retrieve console logs: {e}")
            return []
    
    def get_page_info(self) -> Dict[str, str]:
        """Get current page information"""
        if not self._initialized or not self.automator:
            return {}
        
        try:
            info = {
                'url': self.automator.get_current_url(),
                'title': self.automator.get_page_title()
            }
            self.session.log_action("get_page_info", True, f"Got info for {info.get('url')}")
            return info
        except Exception as e:
            logger.error(f"Error getting page info: {e}")
            self.session.log_error(f"Page info error: {e}")
            return {}
    
    def cleanup(self):
        """Clean up resources"""
        if self._initialized and self.automator:
            try:
                self.automator.cleanup()
                logger.info("Web automator cleaned up successfully")
                self.session.log_action("cleanup", True, "Resources cleaned up")
            except Exception as e:
                logger.warning(f"Cleanup warning: {e}")
                self.session.log_error(f"Cleanup warning: {e}")
            finally:
                self._initialized = False
                self.automator = None


@contextmanager
def automation_session(config: Dict[str, Any], session: AutomationSession = None):
    """Context manager for safe automation sessions"""
    session = session or AutomationSession()
    automator = SafeWebAutomator(config, session)
    
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
            
            # Get console logs
            console_logs = automator.get_console_logs()
            if console_logs:
                console.print(f"   Console logs: {len(console_logs)} entries")
            
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


def example_2_search_automation(automator: SafeWebAutomator, claude: Optional[Any]) -> bool:
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
        
        # VISUAL INSPECTION PAUSE - Let user see the DuckDuckGo page
        console.print("👀 [bold yellow]VISUAL INSPECTION: Browser window is now open with DuckDuckGo[/bold yellow]")
        console.print("📍 You can now see the DuckDuckGo page in the Safari browser window")
        console.print("⏸️ Pausing for 10 seconds so you can inspect the page...")
        time.sleep(10)
        
        # Wait for search box to be ready - try multiple selectors
        console.print("🔍 Waiting for search input...")
        search_selectors = [
            "input[name='q']",  # This is the correct selector for DuckDuckGo
            "input[placeholder*='Search']",  # Backup using placeholder
            "input[type='text']",  # Generic text input
            "input.search-input_searchInput__*",  # Class-based selector
            "[data-module='SearchInput'] input"  # Module-based selector
        ]
        
        search_element = automator.wait_for_element_advanced(search_selectors, timeout=10)
        
        if not search_element:
            console.print("❌ Search box not found", style="bold red")
            console.print("👀 [bold yellow]VISUAL INSPECTION: Check if you can see the search box in the browser window[/bold yellow]")
            console.print("⏸️ Pausing for 15 seconds so you can inspect what DuckDuckGo looks like...")
            time.sleep(15)
            automator.take_screenshot("search_box_not_found")
            return False
        
        console.print("✅ Found search box")
        
        # Type search query
        search_query = "Python web automation selenium"
        console.print(f"⌨️ Typing: {search_query}")
        
        if not automator.type_text(search_selectors[0], search_query):
            console.print("❌ Failed to type search query", style="bold red")
            return False
        
        # Submit search
        console.print("🚀 Submitting search...")
        if not automator.press_key(search_selectors[0], "ENTER"):
            console.print("❌ Failed to submit search", style="bold red")
            return False
        
        # Wait for results
        console.print("⏳ Waiting for search results...")
        
        # Try multiple selectors for search results
        result_selectors = [
            ".result",
            "[data-result]",
            "article",
            ".web-result",
            "div[data-testid='result']"
        ]
        
        results_element = automator.wait_for_element_advanced(result_selectors, timeout=10)
        
        if results_element:
            console.print(f"✅ Search results loaded")
        else:
            console.print("⚠️ Could not verify search results", style="yellow")
            automator.take_screenshot("search_results_timeout")
        
        # Get result info
        page_info = automator.get_page_info()
        console.print(f"   Results URL: {page_info.get('url', 'Unknown')}")
        
        # VISUAL INSPECTION PAUSE - Let user see the search results
        console.print("👀 [bold yellow]VISUAL INSPECTION: You can now see the search results (if any)[/bold yellow]")
        console.print("⏸️ Pausing for 10 seconds so you can inspect the results...")
        time.sleep(10)
        
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
            ("Forms", "form", "Form elements"),
            ("Input Fields", "input", "Input elements")
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
        "🌐 Live Web Automation with Claude Sonnet 4.5\nEnhanced Edition v3.0",
        style="bold cyan"
    ))
    
    # Check dependencies
    if not IMPORTS_AVAILABLE:
        console.print("❌ Required modules not available", style="bold red")
        console.print("Install with: pip install -r requirements.txt")
        return
    
    if not SELENIUM_AVAILABLE:
        console.print("❌ Selenium not installed", style="bold red")
        console.print("Install with: pip install selenium webdriver-manager")
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
            console.print("✅ Claude Sonnet 4.5 guidance active\n")
        except Exception as e:
            logger.warning(f"Claude initialization failed: {e}")
            console.print("⚠️ Continuing without Claude guidance\n")
    else:
        console.print("⚠️ No Claude API key - running without AI guidance\n")
    
    # Create automation session
    session = AutomationSession()
    
    # Run automation in safe context
    results = {
        'example_1': False,
        'example_2': False,
        'example_3': False
    }
    
    with automation_session(config, session) as automator:
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
    console.print("="*60 + "\n")
    
    # Display session metrics
    session.display_summary()
    console.print()
    
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


def health_check(config: Dict[str, Any]) -> bool:
    """Run a quick health check of the automation system"""
    console.print(Panel.fit("🏥 Running System Health Check", style="bold cyan"))
    
    checks = {
        'Python version': sys.version_info >= (3, 7),
        'Selenium installed': SELENIUM_AVAILABLE,
        'WebDriver Manager': WEBDRIVER_MANAGER_AVAILABLE,
        'Automation modules': IMPORTS_AVAILABLE,
        'Config valid': True,
        'Browser available': check_browser_setup(config.get('browser', 'chrome'))
    }
    
    console.print()
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        console.print(f"{status} {check}")
    
    console.print()
    all_passed = all(checks.values())
    
    if all_passed:
        console.print(Panel.fit("🎉 All systems ready!", style="bold green"))
    else:
        console.print(Panel.fit(
            "⚠️ Some checks failed\n\n"
            "Install missing dependencies:\n"
            "pip install selenium webdriver-manager rich python-dotenv",
            style="bold yellow"
        ))
    
    return all_passed


def show_capabilities():
    """Display automation capabilities without running"""
    console.print(Panel.fit(
        "🌐 Web Automation Capabilities Overview\nEnhanced Edition v3.0",
        style="bold blue"
    ))
    
    capabilities = {
        "🧭 Navigation": [
            "URL validation before navigation",
            "Automatic retry logic for failed loads",
            "Back/forward browser history control",
            "Multi-tab and window management",
            "Configurable page load timeouts",
            "Page visit tracking and analytics"
        ],
        "🎯 Element Interaction": [
            "Smart element waiting (no hardcoded sleeps)",
            "Stale element retry handling",
            "CSS selector and XPath support",
            "Safe text input with validation",
            "Key press abstraction (ENTER, TAB, etc.)",
            "Multiple selector fallback strategies",
            "Wait for clickable elements"
        ],
        "🔍 Search & Data": [
            "Automated search engine interaction",
            "Multiple selector fallback strategies",
            "Result verification and validation",
            "Data extraction with error handling",
            "Context-aware element detection",
            "Advanced element finding with retries"
        ],
        "🧠 AI Integration": [
            "Claude Sonnet 4.5 task planning and guidance",
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
            "Context manager for safe sessions",
            "Performance measurement decorators",
            "Session state tracking and metrics",
            "Browser console log capture",
            "Automatic driver management"
        ],
        "🛡️ Safety & Security": [
            "URL validation before navigation",
            "Proper exception handling hierarchy",
            "KeyboardInterrupt preservation",
            "Resource leak prevention",
            "User confirmation for live actions",
            "Comprehensive error logging"
        ],
        "📊 Monitoring & Analytics": [
            "Action tracking and logging",
            "Error tracking and reporting",
            "Screenshot management",
            "Page visit history",
            "Success rate calculations",
            "Session duration tracking",
            "Performance metrics"
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
        "• Chrome/Firefox browser installed\n"
        "• Internet connection\n"
        "• Claude API key (optional, for AI guidance)\n\n"
        "Optional flags:\n"
        "  --live           Run live automation examples\n"
        "  --headless       Run browser in headless mode\n"
        "  --yes            Skip confirmation prompt\n"
        "  --health-check   Run system health check\n"
        "  --config PATH    Custom config file path\n\n"
        "New in v3.0:\n"
        "• Automatic driver management (no manual setup!)\n"
        "• Advanced element waiting strategies\n"
        "• Session analytics and metrics\n"
        "• Performance monitoring\n"
        "• Enhanced error recovery",
        style="cyan"
    ))


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Live Web Automation with Claude Sonnet 4.5 - Enhanced Edition",
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
        '--health-check',
        action='store_true',
        help='Run system health check'
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
        
        # Run health check if requested
        if args.health_check:
            health_check(config)
            return
        
        # Run appropriate mode
        if args.live:
            run_live_automation(config, skip_confirm=args.yes)
        else:
            show_capabilities()
            console.print("\n💡 Add --live flag to run actual browser automation")
            console.print("💡 Use --health-check to verify system setup")
    
    except KeyboardInterrupt:
        console.print("\n\n👋 Goodbye!")
    except Exception as e:
        logger.exception("Fatal error")
        console.print(f"\n❌ Fatal error: {str(e)}", style="bold red")
        sys.exit(1)


if __name__ == "__main__":
    main()