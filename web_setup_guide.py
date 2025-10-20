#!/usr/bin/env python3
"""
Web Automation Setup & Diagnostics Tool - Production Ready
Complete system analysis, dependency checking, and automated setup
"""

import os
import sys
import json
import platform
import subprocess
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from urllib.request import urlopen
from urllib.error import URLError

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.logging import RichHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, show_time=False)]
)
logger = logging.getLogger(__name__)

console = Console()


@dataclass
class BrowserInfo:
    """Browser detection information"""
    name: str
    available: bool
    path: Optional[str]
    version: Optional[str]
    driver_available: bool
    driver_version: Optional[str]
    message: str


@dataclass
class SystemInfo:
    """System information"""
    os: str
    os_version: str
    python_version: str
    architecture: str
    in_virtualenv: bool
    is_wsl: bool
    is_docker: bool


class NetworkChecker:
    """Check network connectivity"""
    
    @staticmethod
    def check_internet() -> bool:
        """Check if internet is available"""
        test_urls = [
            "https://www.google.com",
            "https://www.cloudflare.com",
            "https://1.1.1.1"
        ]
        
        for url in test_urls:
            try:
                urlopen(url, timeout=5)
                return True
            except (URLError, Exception):
                continue
        
        return False
    
    @staticmethod
    def check_pypi() -> bool:
        """Check if PyPI is accessible"""
        try:
            urlopen("https://pypi.org", timeout=5)
            return True
        except (URLError, Exception):
            return False


class SystemDetector:
    """Detect system information and environment"""
    
    @staticmethod
    def detect() -> SystemInfo:
        """Detect comprehensive system information"""
        return SystemInfo(
            os=platform.system(),
            os_version=platform.version(),
            python_version=sys.version.split()[0],
            architecture=platform.machine(),
            in_virtualenv=SystemDetector._check_virtualenv(),
            is_wsl=SystemDetector._check_wsl(),
            is_docker=SystemDetector._check_docker()
        )
    
    @staticmethod
    def _check_virtualenv() -> bool:
        """Check if running in virtual environment"""
        return sys.prefix != sys.base_prefix
    
    @staticmethod
    def _check_wsl() -> bool:
        """Check if running in Windows Subsystem for Linux"""
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower()
        except (FileNotFoundError, PermissionError):
            return False
    
    @staticmethod
    def _check_docker() -> bool:
        """Check if running in Docker container"""
        return os.path.exists('/.dockerenv') or os.path.exists('/run/.containerenv')


class BrowserDetector:
    """Detect installed browsers and their drivers"""
    
    BROWSER_PATHS = {
        "Chrome": {
            "Darwin": [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            ],
            "Windows": [
                "C:/Program Files/Google/Chrome/Application/chrome.exe",
                "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
            ],
            "Linux": [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/snap/bin/chromium",
                "/usr/bin/google-chrome-stable"
            ]
        },
        "Firefox": {
            "Darwin": [
                "/Applications/Firefox.app/Contents/MacOS/firefox"
            ],
            "Windows": [
                "C:/Program Files/Mozilla Firefox/firefox.exe",
                "C:/Program Files (x86)/Mozilla Firefox/firefox.exe"
            ],
            "Linux": [
                "/usr/bin/firefox",
                "/snap/bin/firefox"
            ]
        },
        "Edge": {
            "Darwin": [
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
            ],
            "Windows": [
                "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
                "C:/Program Files/Microsoft/Edge/Application/msedge.exe"
            ],
            "Linux": [
                "/usr/bin/microsoft-edge",
                "/usr/bin/microsoft-edge-stable"
            ]
        },
        "Safari": {
            "Darwin": [
                "/Applications/Safari.app/Contents/MacOS/Safari"
            ]
        }
    }
    
    @classmethod
    def detect_all(cls) -> List[BrowserInfo]:
        """Detect all browsers and their drivers"""
        system_os = platform.system()
        browsers = []
        
        for browser_name, paths_by_os in cls.BROWSER_PATHS.items():
            # Skip Safari on non-macOS
            if browser_name == "Safari" and system_os != "Darwin":
                continue
            
            browser_paths = paths_by_os.get(system_os, [])
            browser_info = cls._detect_browser(browser_name, browser_paths)
            browsers.append(browser_info)
        
        return browsers
    
    @classmethod
    def _detect_browser(cls, name: str, paths: List[str]) -> BrowserInfo:
        """Detect a specific browser"""
        # Find browser binary
        browser_path = None
        for path in paths:
            if os.path.exists(path):
                browser_path = path
                break
        
        # If not found in standard paths, try which/where
        if not browser_path:
            browser_path = shutil.which(name.lower())
        
        browser_available = browser_path is not None
        browser_version = cls._get_browser_version(name, browser_path) if browser_available else None
        
        # Check driver
        driver_available = False
        driver_version = None
        
        if browser_available:
            driver_available, driver_version = cls._check_driver(name)
        
        # Generate message
        if not browser_available:
            message = "Not installed"
        elif not driver_available:
            message = "Browser found, driver needs setup"
        else:
            message = "Ready for automation"
        
        return BrowserInfo(
            name=name,
            available=browser_available,
            path=browser_path,
            version=browser_version,
            driver_available=driver_available,
            driver_version=driver_version,
            message=message
        )
    
    @staticmethod
    def _get_browser_version(name: str, path: Optional[str]) -> Optional[str]:
        """Get browser version"""
        if not path:
            return None
        
        try:
            if name == "Chrome":
                result = subprocess.run([path, "--version"], 
                                      capture_output=True, text=True, timeout=5)
                return result.stdout.strip()
            elif name == "Firefox":
                result = subprocess.run([path, "--version"],
                                      capture_output=True, text=True, timeout=5)
                return result.stdout.strip()
            elif name == "Edge":
                result = subprocess.run([path, "--version"],
                                      capture_output=True, text=True, timeout=5)
                return result.stdout.strip()
            elif name == "Safari":
                # Safari version detection is complex, skip for now
                return "System version"
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return None
        
        return None
    
    @staticmethod
    def _check_driver(name: str) -> Tuple[bool, Optional[str]]:
        """Check if WebDriver is available"""
        try:
            # Try to use webdriver-manager
            if name == "Chrome":
                from webdriver_manager.chrome import ChromeDriverManager
                driver_path = ChromeDriverManager().install()
                return True, driver_path
            elif name == "Firefox":
                from webdriver_manager.firefox import GeckoDriverManager
                driver_path = GeckoDriverManager().install()
                return True, driver_path
            elif name == "Edge":
                from webdriver_manager.microsoft import EdgeChromiumDriverManager
                driver_path = EdgeChromiumDriverManager().install()
                return True, driver_path
            elif name == "Safari":
                # Check if safaridriver is enabled
                result = subprocess.run(["which", "safaridriver"],
                                      capture_output=True, text=True)
                return result.returncode == 0, "System safaridriver"
        except ImportError:
            # webdriver-manager not installed
            return False, None
        except Exception as e:
            logger.debug(f"Driver check failed for {name}: {e}")
            return False, None
        
        return False, None


class PackageChecker:
    """Check Python package installation and versions"""
    
    REQUIRED_PACKAGES = {
        "selenium": {"min_version": "4.0.0", "description": "Browser automation framework"},
        "webdriver-manager": {"min_version": "3.0.0", "description": "Automatic driver management"},
        "requests": {"min_version": "2.0.0", "description": "HTTP requests library"},
        "rich": {"min_version": "10.0.0", "description": "Terminal UI formatting"},
        "python-dotenv": {"min_version": "0.19.0", "description": "Environment variable management"}
    }
    
    @classmethod
    def check_all(cls) -> Dict[str, Dict]:
        """Check all required packages"""
        results = {}
        
        for package, info in cls.REQUIRED_PACKAGES.items():
            package_import = package.replace('-', '_')
            
            try:
                module = __import__(package_import)
                version = getattr(module, '__version__', 'unknown')
                
                results[package] = {
                    'installed': True,
                    'version': version,
                    'description': info['description'],
                    'meets_requirement': cls._version_check(version, info['min_version'])
                }
            except ImportError:
                results[package] = {
                    'installed': False,
                    'version': None,
                    'description': info['description'],
                    'meets_requirement': False
                }
        
        return results
    
    @staticmethod
    def _version_check(current: str, minimum: str) -> bool:
        """Check if current version meets minimum requirement"""
        if current == 'unknown':
            return True  # Can't verify, assume OK
        
        try:
            from packaging import version
            return version.parse(current) >= version.parse(minimum)
        except (ImportError, Exception):
            # If packaging not available, do simple string comparison
            try:
                current_parts = [int(x) for x in current.split('.')[:3]]
                minimum_parts = [int(x) for x in minimum.split('.')[:3]]
                return current_parts >= minimum_parts
            except (ValueError, IndexError):
                return True  # Can't compare, assume OK


class SetupManager:
    """Manage installation and setup"""
    
    @staticmethod
    def install_packages(packages: List[str]) -> bool:
        """Install missing packages"""
        try:
            console.print(f"\n📦 Installing packages: {', '.join(packages)}")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Installing packages...", total=None)
                
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--upgrade"] + packages,
                    capture_output=True,
                    text=True
                )
                
                progress.remove_task(task)
            
            if result.returncode == 0:
                console.print("✅ Packages installed successfully")
                return True
            else:
                console.print(f"❌ Installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Package installation failed: {e}")
            return False
    
    @staticmethod
    def setup_safari_driver() -> bool:
        """Setup Safari WebDriver (macOS only)"""
        if platform.system() != "Darwin":
            return False
        
        console.print("\n🦁 Setting up Safari WebDriver...")
        console.print("   This requires administrator privileges")
        
        try:
            result = subprocess.run(
                ["sudo", "safaridriver", "--enable"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                console.print("✅ Safari WebDriver enabled")
                return True
            else:
                console.print(f"❌ Failed to enable Safari WebDriver")
                return False
                
        except Exception as e:
            logger.error(f"Safari setup failed: {e}")
            return False
    
    @staticmethod
    def create_sample_script(overwrite: bool = False) -> bool:
        """Create a sample automation script"""
        filename = "sample_web_automation.py"
        
        if os.path.exists(filename) and not overwrite:
            if not Confirm.ask(f"{filename} exists. Overwrite?"):
                console.print("⏭️  Skipped sample script creation")
                return False
        
        sample_script = '''#!/usr/bin/env python3
"""
Sample Web Automation Script
A complete, working example using modern Selenium 4+ API
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


def automated_search_example():
    """Example: Automated search with proper waits and error handling"""
    
    # Setup Chrome with automatic driver management
    print("🔧 Setting up browser...")
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Uncomment for headless mode:
    # options.add_argument("--headless")
    
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)
    
    try:
        # Navigate to DuckDuckGo (no cookie consent issues)
        print("🌐 Navigating to DuckDuckGo...")
        driver.get("https://duckduckgo.com")
        
        # Wait for and find search box
        print("🔍 Finding search box...")
        search_box = wait.until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        
        # Type search query
        search_query = "Python web automation best practices"
        print(f"⌨️  Typing: {search_query}")
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        
        # Wait for results to load
        print("⏳ Waiting for results...")
        try:
            results = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-result='result']"))
            )
            print(f"✅ Found {len(results)} search results")
            
            # Extract and display first 3 results
            print("\\n📋 Top Results:")
            for i, result in enumerate(results[:3], 1):
                try:
                    title = result.find_element(By.CSS_SELECTOR, "h2").text
                    print(f"   {i}. {title}")
                except NoSuchElementException:
                    continue
            
        except TimeoutException:
            print("⚠️  Results took too long to load")
        
        # Pause to see results
        print("\\n⏱️  Pausing for 3 seconds...")
        time.sleep(3)
        
        print("✅ Automation completed successfully!")
        
    except TimeoutException as e:
        print(f"❌ Timeout error: Element not found in time")
    except NoSuchElementException as e:
        print(f"❌ Element not found: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
    finally:
        print("🧹 Closing browser...")
        driver.quit()
        print("👋 Done!")


def main():
    """Run the example"""
    print("="*60)
    print("🚀 Web Automation Example - Modern Selenium 4+")
    print("="*60 + "\\n")
    
    try:
        automated_search_example()
    except KeyboardInterrupt:
        print("\\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\\n❌ Fatal error: {e}")


if __name__ == "__main__":
    main()
'''
        
        try:
            with open(filename, 'w') as f:
                f.write(sample_script)
            
            # Make executable on Unix-like systems
            if platform.system() in ["Darwin", "Linux"]:
                os.chmod(filename, 0o755)
            
            console.print(f"✅ Sample script created: {filename}")
            console.print(f"   Run with: python {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create sample script: {e}")
            return False
    
    @staticmethod
    def create_config_file() -> bool:
        """Create default configuration file"""
        config = {
            "browser": "chrome",
            "headless": False,
            "wait_timeout": 10,
            "max_retries": 3,
            "screenshot_on_error": True,
            "page_load_timeout": 30,
            "implicit_wait": 0,
            "window_size": [1920, 1080]
        }
        
        filename = "config.json"
        
        if os.path.exists(filename):
            if not Confirm.ask(f"{filename} exists. Overwrite?"):
                return False
        
        try:
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
            
            console.print(f"✅ Configuration created: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create config: {e}")
            return False


def display_system_info(system_info: SystemInfo):
    """Display system information"""
    console.print(Panel.fit("🔍 System Information", style="bold cyan"))
    
    table = Table(show_header=False, box=None)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Operating System", f"{system_info.os} {system_info.architecture}")
    table.add_row("OS Version", system_info.os_version)
    table.add_row("Python Version", system_info.python_version)
    table.add_row("Virtual Environment", "✅ Active" if system_info.in_virtualenv else "❌ Not active")
    
    if system_info.is_wsl:
        table.add_row("Environment", "🐧 Windows Subsystem for Linux")
    elif system_info.is_docker:
        table.add_row("Environment", "🐳 Docker Container")
    else:
        table.add_row("Environment", "💻 Native")
    
    console.print(table)
    
    # Virtual environment warning
    if not system_info.in_virtualenv:
        console.print("\n⚠️  [yellow]Not running in a virtual environment[/yellow]")
        console.print("   Consider creating one: python -m venv venv")
        console.print("   Activate: source venv/bin/activate (Unix) or venv\\Scripts\\activate (Windows)")


def display_browser_info(browsers: List[BrowserInfo]):
    """Display browser detection results"""
    console.print("\n" + "="*60)
    console.print(Panel.fit("🌐 Browser Detection Results", style="bold green"))
    
    table = Table(show_header=True)
    table.add_column("Browser", style="cyan", width=12)
    table.add_column("Status", width=10)
    table.add_column("Version", width=15)
    table.add_column("Driver", width=10)
    table.add_column("Message", style="dim")
    
    for browser in browsers:
        status_icon = "✅" if browser.available else "❌"
        driver_icon = "✅" if browser.driver_available else "❌"
        version = browser.version or "N/A"
        
        table.add_row(
            browser.name,
            status_icon,
            version,
            driver_icon,
            browser.message
        )
    
    console.print(table)
    
    # Recommendations
    available_browsers = [b for b in browsers if b.available and b.driver_available]
    if available_browsers:
        console.print(f"\n✅ {len(available_browsers)} browser(s) ready for automation")
    else:
        console.print("\n⚠️  [yellow]No browsers ready for automation[/yellow]")


def display_package_info(packages: Dict[str, Dict]):
    """Display package check results"""
    console.print("\n" + "="*60)
    console.print(Panel.fit("📦 Python Package Status", style="bold blue"))
    
    table = Table(show_header=True)
    table.add_column("Package", style="cyan", width=20)
    table.add_column("Status", width=10)
    table.add_column("Version", width=12)
    table.add_column("Description", style="dim")
    
    missing_packages = []
    outdated_packages = []
    
    for package, info in packages.items():
        if info['installed']:
            status = "✅"
            if not info['meets_requirement']:
                status = "⚠️"
                outdated_packages.append(package)
        else:
            status = "❌"
            missing_packages.append(package)
        
        version = info['version'] or "N/A"
        
        table.add_row(
            package,
            status,
            version,
            info['description']
        )
    
    console.print(table)
    
    return missing_packages, outdated_packages


def display_network_status():
    """Display network connectivity status"""
    console.print("\n" + "="*60)
    console.print(Panel.fit("🌍 Network Connectivity", style="bold magenta"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Checking connectivity...", total=None)
        
        internet_ok = NetworkChecker.check_internet()
        pypi_ok = NetworkChecker.check_pypi()
        
        progress.remove_task(task)
    
    table = Table(show_header=False, box=None)
    table.add_column("Service", style="cyan", width=20)
    table.add_column("Status", width=40)
    
    table.add_row(
        "Internet",
        "✅ Connected" if internet_ok else "❌ Not connected"
    )
    table.add_row(
        "PyPI (pypi.org)",
        "✅ Accessible" if pypi_ok else "❌ Not accessible"
    )
    
    console.print(table)
    
    if not internet_ok:
        console.print("\n⚠️  [yellow]No internet connection detected[/yellow]")
        console.print("   Some features may not work without internet")
    
    return internet_ok and pypi_ok


def show_installation_instructions(system_info: SystemInfo, browsers: List[BrowserInfo]):
    """Show platform-specific installation instructions"""
    console.print("\n" + "="*60)
    console.print(Panel.fit("📋 Installation Instructions", style="bold yellow"))
    
    os_name = system_info.os
    
    # Browser installation
    missing_browsers = [b for b in browsers if not b.available]
    if missing_browsers:
        console.print("\n🌐 Install Missing Browsers:")
        
        if os_name == "Darwin":  # macOS
            console.print("   # Using Homebrew:")
            for browser in missing_browsers:
                if browser.name == "Chrome":
                    console.print("   brew install --cask google-chrome")
                elif browser.name == "Firefox":
                    console.print("   brew install --cask firefox")
                elif browser.name == "Edge":
                    console.print("   brew install --cask microsoft-edge")
        
        elif os_name == "Linux":
            console.print("   # Using apt (Ubuntu/Debian):")
            for browser in missing_browsers:
                if browser.name == "Chrome":
                    console.print("   wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
                    console.print("   sudo dpkg -i google-chrome-stable_current_amd64.deb")
                elif browser.name == "Firefox":
                    console.print("   sudo apt install firefox")
        
        elif os_name == "Windows":
            console.print("   Download from browser websites:")
            for browser in missing_browsers:
                if browser.name == "Chrome":
                    console.print("   https://www.google.com/chrome/")
                elif browser.name == "Firefox":
                    console.print("   https://www.mozilla.org/firefox/")
                elif browser.name == "Edge":
                    console.print("   https://www.microsoft.com/edge/")
    
    # WebDriver setup
    console.print("\n🔧 WebDriver Setup:")
    console.print("   # Automatic (recommended):")
    console.print("   pip install webdriver-manager")
    console.print("   # Drivers will be downloaded automatically on first use")


def interactive_setup():
    """Interactive setup wizard"""
    console.print(Panel.fit(
        "🧙 Interactive Setup Wizard",
        style="bold white"
    ))
    
    # Check packages
    console.print("\n📦 Checking Python packages...")
    packages = PackageChecker.check_all()
    missing_packages, outdated_packages = display_package_info(packages)
    
    # Offer to install missing packages
    if missing_packages:
        console.print(f"\n⚠️  Missing {len(missing_packages)} package(s)")
        if Confirm.ask("Install missing packages now?"):
            if SetupManager.install_packages(missing_packages):
                console.print("✅ Installation complete!")
            else:
                console.print("❌ Installation failed - manual installation required")
    
    # Offer to upgrade outdated packages
    if outdated_packages:
        console.print(f"\n⚠️  {len(outdated_packages)} package(s) may need upgrading")
        if Confirm.ask("Upgrade outdated packages?"):
            SetupManager.install_packages(outdated_packages)
    
    # Safari setup (macOS only)
    if platform.system() == "Darwin":
        browsers = BrowserDetector.detect_all()
        safari = next((b for b in browsers if b.name == "Safari"), None)
        
        if safari and safari.available and not safari.driver_available:
            if Confirm.ask("\nSetup Safari WebDriver? (requires sudo)"):
                SetupManager.setup_safari_driver()
    
    # Create sample files
    console.print("\n📝 Sample Files:")
    if Confirm.ask("Create sample automation script?"):
        SetupManager.create_sample_script()
    
    if Confirm.ask("Create default configuration file?"):
        SetupManager.create_config_file()


def main():
    """Main setup and diagnostic tool"""
    console.print(Panel.fit(
        "🌐 Web Automation Setup & Diagnostics Tool\n"
        "Complete system analysis and automated setup",
        style="bold white"
    ))
    
    try:
        # System detection
        console.print("\n🔍 Detecting system information...")
        system_info = SystemDetector.detect()
        display_system_info(system_info)
        
        # Network check
        network_ok = display_network_status()
        
        # Browser detection
        console.print("\n🌐 Detecting browsers and drivers...")
        browsers = BrowserDetector.detect_all()
        display_browser_info(browsers)
        
        # Package check
        console.print("\n📦 Checking Python packages...")
        packages = PackageChecker.check_all()
        missing_packages, outdated_packages = display_package_info(packages)
        
        # Installation instructions
        if missing_packages or outdated_packages or not any(b.driver_available for b in browsers):
            show_installation_instructions(system_info, browsers)
        
        # Summary
        console.print("\n" + "="*60)
        ready_browsers = sum(1 for b in browsers if b.available and b.driver_available)
        ready_packages = sum(1 for p in packages.values() if p['installed'] and p['meets_requirement'])
        
        if ready_browsers > 0 and len(missing_packages) == 0:
            console.print(Panel.fit(
                f"🎉 Setup Complete!\n\n"
                f"✅ {ready_browsers} browser(s) ready\n"
                f"✅ {ready_packages}/{len(packages)} packages ready\n"
                f"✅ Network: {'Connected' if network_ok else 'Limited'}\n\n"
                f"Ready to run web automation!",
                style="bold green"
            ))
        else:
            console.print(Panel.fit(
                f"⚠️  Setup Incomplete\n\n"
                f"🌐 Browsers ready: {ready_browsers}\n"
                f"📦 Missing packages: {len(missing_packages)}\n"
                f"🌍 Network: {'Connected' if network_ok else 'Disconnected'}\n\n"
                f"Follow the instructions above to complete setup",
                style="bold yellow"
            ))
        
        # Offer interactive setup
        if missing_packages or outdated_packages:
            console.print()
            if Confirm.ask("Run interactive setup wizard?"):
                interactive_setup()
        
    except KeyboardInterrupt:
        console.print("\n\n👋 Setup cancelled by user")
    except Exception as e:
        logger.exception("Setup failed")
        console.print(f"\n❌ Setup error: {e}"), style="bold red"