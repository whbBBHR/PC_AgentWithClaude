#!/usr/bin/env python3
"""
Enhanced Web Automation with Smart Browser Detection - Production Ready
Automatic browser detection, WebDriver management, and robust error handling
"""

import os
import sys
import json
import time
import shutil
import logging
import platform
import subprocess
from typing import Optional, List, Tuple, Dict, Any
from pathlib import Path
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from urllib.request import urlopen
from urllib.error import URLError

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.logging import RichHandler

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


@dataclass
class BrowserTestResult:
    """Result of browser automation test"""
    browser_type: str
    success: bool
    error_message: Optional[str] = None
    page_title: Optional[str] = None
    page_url: Optional[str] = None
    driver_version: Optional[str] = None


class NetworkChecker:
    """Check network connectivity before automation"""
    
    @staticmethod
    def check_internet(timeout: int = 5) -> bool:
        """Check if internet connection is available"""
        test_urls = [
            "https://www.google.com",
            "https://example.com",
            "https://1.1.1.1"
        ]
        
        for url in test_urls:
            try:
                urlopen(url, timeout=timeout)
                logger.info(f"Network check passed: {url}")
                return True
            except (URLError, Exception) as e:
                logger.debug(f"Network check failed for {url}: {e}")
                continue
        
        return False


class BrowserDetector:
    """Detect available browsers on the system"""
    
    @staticmethod
    def find_chrome() -> bool:
        """Find Chrome browser"""
        # Try shutil.which first (most reliable)
        if shutil.which("google-chrome") or shutil.which("chrome"):
            return True
        
        # Check standard paths
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Google Chrome.app",
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/snap/bin/chromium",
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        ]
        
        # Check user directories
        home = Path.home()
        chrome_paths.extend([
            str(home / "Applications" / "Google Chrome.app"),
            str(home / ".local" / "bin" / "google-chrome")
        ])
        
        return any(os.path.exists(path) for path in chrome_paths)
    
    @staticmethod
    def find_firefox() -> bool:
        """Find Firefox browser"""
        if shutil.which("firefox"):
            return True
        
        firefox_paths = [
            "/Applications/Firefox.app",
            "/usr/bin/firefox",
            "/snap/bin/firefox",
            "C:/Program Files/Mozilla Firefox/firefox.exe",
            "C:/Program Files (x86)/Mozilla Firefox/firefox.exe"
        ]
        
        return any(os.path.exists(path) for path in firefox_paths)
    
    @staticmethod
    def find_safari() -> bool:
        """Find Safari browser (macOS only)"""
        if platform.system() != "Darwin":
            return False
        
        return os.path.exists("/Applications/Safari.app")
    
    @staticmethod
    def find_edge() -> bool:
        """Find Edge browser"""
        if shutil.which("microsoft-edge"):
            return True
        
        edge_paths = [
            "/Applications/Microsoft Edge.app",
            "/usr/bin/microsoft-edge",
            "/usr/bin/microsoft-edge-stable",
            "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
            "C:/Program Files/Microsoft/Edge/Application/msedge.exe"
        ]
        
        return any(os.path.exists(path) for path in edge_paths)
    
    @classmethod
    def detect_all_browsers(cls) -> List[Tuple[str, str, bool]]:
        """
        Detect all available browsers
        Returns: List of (browser_type, description, available)
        """
        browsers = [
            ("chrome", "Chrome with auto WebDriver management", cls.find_chrome()),
            ("firefox", "Firefox with auto WebDriver management", cls.find_firefox()),
            ("edge", "Edge with auto WebDriver management", cls.find_edge()),
        ]
        
        # Add Safari for macOS
        if platform.system() == "Darwin":
            browsers.append(("safari", "Safari (requires configuration)", cls.find_safari()))
        
        return browsers


class SeleniumChecker:
    """Check Selenium installation and version"""
    
    @staticmethod
    def check_selenium() -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if Selenium is installed and get version
        Returns: (installed, version, message)
        """
        try:
            import selenium
            version = selenium.__version__
            
            major_version = int(version.split('.')[0])
            
            if major_version >= 4:
                return True, version, "Selenium 4+ installed"
            else:
                return True, version, "Selenium 3.x detected - upgrade recommended"
                
        except ImportError:
            return False, None, "Selenium not installed"
        except Exception as e:
            return False, None, f"Selenium check failed: {e}"
    
    @staticmethod
    def check_webdriver_manager() -> bool:
        """Check if webdriver-manager is installed"""
        try:
            import webdriver_manager
            return True
        except ImportError:
            return False


class ConfigManager:
    """Manage configuration files safely"""
    
    @staticmethod
    def load_config(config_path: str = "config.json") -> Dict[str, Any]:
        """Load configuration with error handling"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Config file {config_path} not found, using defaults")
                return ConfigManager.get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config: {e}")
            return ConfigManager.get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return ConfigManager.get_default_config()
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "browser": "chrome",
            "headless": False,
            "wait_timeout": 15,
            "max_retries": 3,
            "screenshot_on_error": True,
            "page_load_timeout": 30,
            "window_size": {"width": 1920, "height": 1080}
        }
    
    @staticmethod
    def save_config(config: Dict[str, Any], config_path: str = "config.json") -> bool:
        """Save configuration safely with backup"""
        try:
            # Create backup if file exists
            if os.path.exists(config_path):
                backup_path = f"{config_path}.backup"
                shutil.copy2(config_path, backup_path)
                logger.info(f"Created backup: {backup_path}")
            
            # Atomic write (write to temp, then rename)
            temp_path = f"{config_path}.tmp"
            with open(temp_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            os.replace(temp_path, config_path)
            logger.info(f"Configuration saved: {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    @staticmethod
    def update_browser_preference(browser_type: str) -> bool:
        """Update config with working browser"""
        config = ConfigManager.load_config()
        config["browser"] = browser_type
        config["last_working_browser"] = browser_type
        config["last_test_date"] = datetime.now().isoformat()
        
        return ConfigManager.save_config(config)


class BrowserAutomationTester:
    """Test browser automation with proper cleanup"""
    
    @staticmethod
    def test_browser(browser_type: str, headless: bool = False) -> BrowserTestResult:
        """
        Test browser automation with comprehensive error handling
        
        Args:
            browser_type: Type of browser to test (chrome, firefox, safari, edge)
            headless: Run in headless mode
            
        Returns:
            BrowserTestResult with test outcome
        """
        console.print(f"🧪 Testing {browser_type} automation...")
        
        # Check dependencies first
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import (
                WebDriverException,
                TimeoutException,
                NoSuchElementException
            )
        except ImportError as e:
            return BrowserTestResult(
                browser_type=browser_type,
                success=False,
                error_message=f"Missing dependency: {e}. Install: pip install selenium"
            )
        
        driver = None
        success = False
        error_msg = None
        title = None
        url = None
        driver_version = None
        
        try:
            # Setup browser based on type
            if browser_type == "chrome":
                driver = BrowserAutomationTester._setup_chrome(headless)
            elif browser_type == "firefox":
                driver = BrowserAutomationTester._setup_firefox(headless)
            elif browser_type == "safari":
                driver = BrowserAutomationTester._setup_safari()
            elif browser_type == "edge":
                driver = BrowserAutomationTester._setup_edge(headless)
            else:
                raise ValueError(f"Unsupported browser: {browser_type}")
            
            if not driver:
                raise Exception("Failed to initialize WebDriver")
            
            console.print(f"✅ {browser_type.capitalize()} WebDriver initialized")
            
            # Get driver version if available
            try:
                if hasattr(driver, 'capabilities'):
                    caps = driver.capabilities
                    driver_version = caps.get('browserVersion', 'unknown')
            except Exception:
                pass
            
            # Test navigation
            console.print("🌐 Testing navigation to example.com...")
            driver.get("https://example.com")
            
            # Wait for page to load
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Get page info
            title = driver.title
            url = driver.current_url
            
            console.print(f"✅ Navigation successful!")
            console.print(f"   Title: {title}")
            console.print(f"   URL: {url}")
            
            success = True
            
            # Brief pause if not headless (let user see)
            if not headless:
                time.sleep(2)
            
        except KeyboardInterrupt:
            error_msg = "Test interrupted by user"
            console.print(f"\n⚠️ {error_msg}")
            raise
        except ImportError as e:
            error_msg = f"Missing dependency: {e}"
            console.print(f"❌ {error_msg}")
        except WebDriverException as e:
            error_msg = f"WebDriver error: {str(e)[:200]}"
            console.print(f"❌ {error_msg}")
        except TimeoutException:
            error_msg = "Page load timeout"
            console.print(f"❌ {error_msg}")
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)[:200]}"
            console.print(f"❌ {error_msg}")
            logger.exception(f"{browser_type} test failed")
        
        finally:
            # CRITICAL: Always cleanup driver
            if driver:
                try:
                    driver.quit()
                    console.print("🧹 Browser closed")
                except Exception as e:
                    logger.warning(f"Driver cleanup warning: {e}")
        
        return BrowserTestResult(
            browser_type=browser_type,
            success=success,
            error_message=error_msg,
            page_title=title,
            page_url=url,
            driver_version=driver_version
        )
    
    @staticmethod
    def _setup_chrome(headless: bool = False):
        """Setup Chrome with proper configuration"""
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium import webdriver
        
        options = ChromeOptions()
        
        # Essential options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        if headless:
            options.add_argument("--headless=new")
        
        # Window size
        options.add_argument("--window-size=1920,1080")
        
        # Optional: Anti-detection (use sparingly, can violate ToS)
        # options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Automatic ChromeDriver management
        service = ChromeService(ChromeDriverManager().install())
        
        return webdriver.Chrome(service=service, options=options)
    
    @staticmethod
    def _setup_firefox(headless: bool = False):
        """Setup Firefox with proper configuration"""
        from webdriver_manager.firefox import GeckoDriverManager
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium import webdriver
        
        options = FirefoxOptions()
        
        if headless:
            options.add_argument("--headless")
        
        service = FirefoxService(GeckoDriverManager().install())
        
        return webdriver.Firefox(service=service, options=options)
    
    @staticmethod
    def _setup_safari():
        """Setup Safari (macOS only)"""
        from selenium import webdriver
        
        # Safari doesn't support many options
        return webdriver.Safari()
    
    @staticmethod
    def _setup_edge(headless: bool = False):
        """Setup Edge with proper configuration"""
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        from selenium.webdriver.edge.service import Service as EdgeService
        from selenium.webdriver.edge.options import Options as EdgeOptions
        from selenium import webdriver
        
        options = EdgeOptions()
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        if headless:
            options.add_argument("--headless=new")
        
        service = EdgeService(EdgeChromiumDriverManager().install())
        
        return webdriver.Edge(service=service, options=options)


def display_system_status():
    """Display comprehensive system status"""
    console.print(Panel.fit("🔍 System Status Check", style="bold cyan"))
    
    # Python version
    console.print(f"🐍 Python: {sys.version.split()[0]}")
    console.print(f"💻 OS: {platform.system()} {platform.machine()}")
    
    # Virtual environment
    in_venv = sys.prefix != sys.base_prefix
    venv_status = "✅ Active" if in_venv else "⚠️ Not active"
    console.print(f"📦 Virtual Environment: {venv_status}")
    
    if not in_venv:
        console.print("   💡 Consider using: python -m venv venv")
    
    # Network check
    console.print("\n🌍 Network Status:")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Checking connectivity...", total=None)
        network_ok = NetworkChecker.check_internet()
        progress.remove_task(task)
    
    if network_ok:
        console.print("   ✅ Internet connection active")
    else:
        console.print("   ❌ No internet connection")
        console.print("   ⚠️ WebDriver download may fail")
    
    # Selenium check
    console.print("\n📚 Dependencies:")
    selenium_ok, selenium_version, selenium_msg = SeleniumChecker.check_selenium()
    
    if selenium_ok:
        console.print(f"   ✅ Selenium {selenium_version}")
    else:
        console.print(f"   ❌ Selenium: {selenium_msg}")
        console.print("      Install: pip install selenium")
    
    webdriver_manager_ok = SeleniumChecker.check_webdriver_manager()
    if webdriver_manager_ok:
        console.print("   ✅ webdriver-manager installed")
    else:
        console.print("   ❌ webdriver-manager not installed")
        console.print("      Install: pip install webdriver-manager")
    
    return selenium_ok and webdriver_manager_ok and network_ok


def run_smart_browser_detection():
    """Run intelligent browser detection and testing"""
    console.print("\n" + "="*60)
    console.print(Panel.fit("🚀 Smart Browser Detection & Testing", style="bold green"))
    
    # Detect available browsers
    all_browsers = BrowserDetector.detect_all_browsers()
    
    console.print("\n🌐 Browser Detection Results:")
    available_browsers = []
    
    for browser_type, description, available in all_browsers:
        status = "✅" if available else "❌"
        console.print(f"   {status} {description}")
        
        if available:
            available_browsers.append((browser_type, description))
    
    if not available_browsers:
        console.print("\n❌ No browsers found!")
        console.print("\n💡 Install Chrome (recommended):")
        if platform.system() == "Darwin":
            console.print("   brew install --cask google-chrome")
        else:
            console.print("   https://www.google.com/chrome/")
        return None
    
    console.print(f"\n🎯 Found {len(available_browsers)} browser(s) available")
    
    # Test each browser
    console.print("\n" + "="*60)
    console.print("🧪 Testing Browser Automation...\n")
    
    for browser_type, description in available_browsers:
        console.print(f"🔧 Testing {description}...")
        
        result = BrowserAutomationTester.test_browser(browser_type)
        
        if result.success:
            console.print(Panel.fit(
                f"🎉 Success! {browser_type.capitalize()} Automation Working!\n\n"
                f"✅ Browser: {description}\n"
                f"✅ Version: {result.driver_version or 'unknown'}\n"
                f"✅ Navigation: Successful\n"
                f"✅ Page Title: {result.page_title}\n\n"
                f"Configuration updated to use {browser_type}",
                style="bold green"
            ))
            
            # Update config with working browser
            ConfigManager.update_browser_preference(browser_type)
            
            return browser_type
        else:
            console.print(f"⚠️ {browser_type} failed: {result.error_message}\n")
    
    # If we get here, no browsers worked
    console.print(Panel.fit(
        "❌ No Browsers Working\n\n"
        "Possible issues:\n"
        "• Missing dependencies (selenium, webdriver-manager)\n"
        "• Network connectivity problems\n"
        "• Browser/driver compatibility issues\n\n"
        "Try:\n"
        "pip install --upgrade selenium webdriver-manager",
        style="bold red"
    ))
    
    return None


def show_installation_guide():
    """Show comprehensive installation guide"""
    console.print(Panel.fit("📖 Installation & Setup Guide", style="bold blue"))
    
    console.print("\n🌐 Recommended: Google Chrome")
    console.print("   ✅ Best compatibility and reliability")
    console.print("   ✅ Automatic driver management")
    console.print("   ✅ Works on all platforms")
    
    console.print("\n📥 Installation:")
    
    if platform.system() == "Darwin":  # macOS
        console.print("   Option 1 (Homebrew - recommended):")
        console.print("   $ brew install --cask google-chrome")
        console.print("\n   Option 2 (Manual):")
        console.print("   1. Visit https://www.google.com/chrome/")
        console.print("   2. Download and install")
    elif platform.system() == "Linux":
        console.print("   Ubuntu/Debian:")
        console.print("   $ wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
        console.print("   $ sudo dpkg -i google-chrome-stable_current_amd64.deb")
    else:  # Windows
        console.print("   1. Visit https://www.google.com/chrome/")
        console.print("   2. Download and install")
    
    console.print("\n📦 Python Dependencies:")
    console.print("   $ pip install selenium webdriver-manager python-dotenv rich")
    
    console.print("\n🧪 Test Your Setup:")
    console.print("   $ python enhanced_web_automation.py --test")


def main():
    """Main entry point with comprehensive workflow"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Enhanced Web Automation with Smart Browser Detection"
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run browser detection and testing'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run tests in headless mode'
    )
    parser.add_argument(
        '--guide',
        action='store_true',
        help='Show installation guide only'
    )
    
    args = parser.parse_args()
    
    console.print(Panel.fit(
        "🌐 Enhanced Web Automation\n"
        "Smart Browser Detection & Testing",
        style="bold white"
    ))
    
    try:
        if args.guide:
            show_installation_guide()
            return
        
        # System status check
        deps_ok = display_system_status()
        
        if not deps_ok:
            console.print("\n⚠️ Missing dependencies detected")
            if Confirm.ask("Show installation guide?"):
                show_installation_guide()
            return
        
        # Run browser detection and testing
        if args.test or Confirm.ask("\nRun browser detection and testing?"):
            working_browser = run_smart_browser_detection()
            
            if working_browser:
                console.print("\n" + "="*60)
                console.print(Panel.fit(
                    f"✅ Setup Complete!\n\n"
                    f"Working browser: {working_browser}\n"
                    f"Configuration saved\n\n"
                    f"Next steps:\n"
                    f"• Run: python live_web_automation.py --live\n"
                    f"• Or use in your automation scripts",
                    style="bold green"
                ))
            else:
                console.print("\n💡 Need help? Run with --guide flag")
        else:
            show_installation_guide()
    
    except KeyboardInterrupt:
        console.print("\n\n👋 Cancelled by user")
    except Exception as e:
        logger.exception("Unexpected error")
        console.print(f"\n❌ Error: {e}", style="bold red")
        sys.exit(1)


if __name__ == "__main__":
    main()