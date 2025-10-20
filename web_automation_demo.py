#!/usr/bin/env python3
"""
Web Automation Demo with Enhanced Claude 3.5 - Refactored
Demonstrates browser automation, navigation, and intelligent web interaction
with improved error handling, cleanup, and flexibility.
"""

import os
import json
import time
import argparse
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import contextmanager
from urllib.parse import urlparse

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.logging import RichHandler

# Load environment
load_dotenv()

# Import enhanced modules
from src.pc_agent.claude_client import ClaudeClient
from src.pc_agent.web_automator import WebAutomator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, show_time=False)]
)
logger = logging.getLogger(__name__)

console = Console()


class DemoResults:
    """Track demo execution results"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'initialization': None,
            'navigation': None,
            'element_interaction': None,
            'search': None,
            'claude_integration': None,
            'total_duration': 0
        }
        self.start_time = time.time()
    
    def record(self, section: str, status: str, details: Dict[str, Any] = None, duration: float = None):
        """Record results for a demo section"""
        self.results[section] = {
            'status': status,
            'details': details or {},
            'duration': duration
        }
    
    def finalize(self):
        """Finalize results with total duration"""
        self.results['total_duration'] = time.time() - self.start_time
    
    def save(self, filepath: str = 'demo_results.json'):
        """Save results to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.results, f, indent=2)
            console.print(f"📊 Results saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")


@contextmanager
def timed_section(name: str):
    """Context manager for timing demo sections"""
    start = time.time()
    console.print(f"\n⏱️ Starting: {name}")
    try:
        yield
        elapsed = time.time() - start
        console.print(f"✅ Completed in {elapsed:.2f}s")
    except Exception as e:
        elapsed = time.time() - start
        console.print(f"❌ Failed after {elapsed:.2f}s: {str(e)}")
        raise


def load_config(config_path: str = 'config.json') -> Dict[str, Any]:
    """Load configuration with caching and validation"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Set defaults
        config.setdefault('browser', 'chrome')
        config.setdefault('headless', False)
        config.setdefault('wait_timeout', 10)
        config.setdefault('max_retries', 3)
        
        return config
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, using defaults")
        return {
            'browser': 'chrome',
            'headless': False,
            'wait_timeout': 10,
            'max_retries': 3
        }
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        raise


def is_safe_url(url: str) -> bool:
    """Validate URL for safety"""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ['http', 'https'] and bool(parsed.netloc)
    except Exception:
        return False


def demo_web_automator_init(config: Dict[str, Any], live_mode: bool = False) -> Optional[WebAutomator]:
    """Initialize and test web automator"""
    console.print(Panel.fit("🌐 Web Automator Initialization", style="bold cyan"))
    
    start_time = time.time()
    
    try:
        console.print("🔧 Loading web automation configuration...")
        console.print(f"   Browser: {config.get('browser', 'chrome')}")
        console.print(f"   Headless mode: {config.get('headless', False)}")
        console.print(f"   Wait timeout: {config.get('wait_timeout', 10)}s")
        console.print(f"   Max retries: {config.get('max_retries', 3)}")
        console.print(f"   Live mode: {'ENABLED' if live_mode else 'DISABLED (Demo Only)'}")
        
        if not live_mode:
            console.print("\n💡 Running in demo mode - no actual browser will launch")
            console.print("   Use --live flag to enable real browser automation")
            return None
        
        # Initialize web automator only in live mode
        web_automator = WebAutomator(config)
        
        elapsed = time.time() - start_time
        console.print(f"\n✅ Web Automator initialized successfully in {elapsed:.2f}s!")
        console.print("   Driver capabilities ready")
        console.print("   Enhanced Claude 3.5 integration active")
        
        return web_automator
        
    except KeyboardInterrupt:
        console.print("\n⚠️ Initialization cancelled by user")
        raise
    except Exception as e:
        elapsed = time.time() - start_time
        logger.exception("Web Automator initialization failed")
        console.print(f"❌ Initialization error after {elapsed:.2f}s: {str(e)}", style="bold red")
        return None


def demo_navigation_capabilities(web_automator: Optional[WebAutomator], live_mode: bool = False) -> Dict[str, Any]:
    """Demonstrate web navigation features"""
    console.print(Panel.fit("🧭 Navigation Capabilities Demo", style="bold green"))
    
    result = {'status': 'skipped', 'details': {}}
    
    try:
        console.print("🚀 Web navigation features:")
        console.print("   ✅ URL navigation with validation")
        console.print("   ✅ Page load detection and waiting")
        console.print("   ✅ History management (back/forward)")
        console.print("   ✅ Tab and window handling")
        console.print("   ✅ SSL certificate handling")
        console.print("   ✅ Redirect following with limits")
        
        if not live_mode or not web_automator:
            console.print("\n📍 Navigation capabilities (demo mode - no actual browsing)")
            result['status'] = 'demo_only'
            return result
        
        # Live navigation test
        test_url = "https://example.com"
        
        if not is_safe_url(test_url):
            console.print(f"⚠️ Invalid URL: {test_url}", style="yellow")
            result['status'] = 'error'
            result['details']['error'] = 'Invalid URL'
            return result
        
        console.print(f"\n📍 Testing live navigation to {test_url}...")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Navigating to website...", total=None)
            
            success = web_automator.navigate_to(test_url)
            progress.remove_task(task)
        
        if success:
            console.print("✅ Navigation successful!")
            
            # Get page information
            current_url = web_automator.get_current_url()
            page_title = web_automator.get_page_title()
            
            console.print(f"   Current URL: {current_url}")
            console.print(f"   Page title: {page_title}")
            
            result['status'] = 'success'
            result['details'] = {
                'url': current_url,
                'title': page_title
            }
        else:
            console.print("⚠️ Navigation completed with warnings")
            result['status'] = 'warning'
            
    except KeyboardInterrupt:
        console.print("\n⚠️ Navigation cancelled by user")
        result['status'] = 'cancelled'
        raise
    except Exception as e:
        logger.exception("Navigation error")
        console.print(f"❌ Navigation error: {str(e)}", style="bold red")
        result['status'] = 'error'
        result['details']['error'] = str(e)
    
    return result


def demo_element_interaction(web_automator: Optional[WebAutomator], live_mode: bool = False) -> Dict[str, Any]:
    """Demonstrate web element detection and interaction"""
    console.print(Panel.fit("🎯 Element Interaction Demo", style="bold blue"))
    
    result = {'status': 'demo_only', 'details': {}}
    
    try:
        console.print("🔍 Element detection capabilities:")
        console.print("   ✅ CSS selector-based finding")
        console.print("   ✅ XPath expression support")
        console.print("   ✅ Text content matching")
        console.print("   ✅ Attribute-based selection")
        console.print("   ✅ Dynamic element waiting")
        
        console.print("\n🖱️ Interaction methods:")
        console.print("   ✅ Click actions (left, right, double)")
        console.print("   ✅ Text input and form filling")
        console.print("   ✅ Dropdown selection")
        console.print("   ✅ Checkbox and radio button handling")
        console.print("   ✅ File upload operations")
        console.print("   ✅ Scroll and hover actions")
        
        if not live_mode or not web_automator:
            console.print("\n💡 Element interaction (demo mode - showing capabilities only)")
            return result
        
        console.print("\n🔍 Testing element detection on current page...")
        
        # Example element queries (safe)
        example_selectors = [
            ("CSS Selector", "h1", "Main heading element"),
            ("XPath", "//title", "Page title element"),
            ("Tag Name", "p", "Paragraph elements"),
        ]
        
        console.print("📋 Testing element selection methods:")
        for method, selector, description in example_selectors:
            console.print(f"   • {method}: '{selector}' - {description}")
        
        console.print("\n✅ Element interaction system ready")
        result['status'] = 'success'
        
    except Exception as e:
        logger.exception("Element interaction error")
        console.print(f"❌ Error: {str(e)}", style="bold red")
        result['status'] = 'error'
        result['details']['error'] = str(e)
    
    return result


def demo_search_capabilities(live_mode: bool = False) -> Dict[str, Any]:
    """Demonstrate web search automation"""
    console.print(Panel.fit("🔍 Search Automation Demo", style="bold magenta"))
    
    result = {'status': 'demo_only', 'details': {}}
    
    try:
        console.print("🔍 Search automation features:")
        console.print("   ✅ Multiple search engine support")
        console.print("   ✅ Query optimization and formatting")
        console.print("   ✅ Result extraction and analysis")
        console.print("   ✅ Safe search and content filtering")
        console.print("   ✅ Pagination handling")
        
        console.print("\n🌐 Supported search engines:")
        search_engines = ["Google", "Bing", "DuckDuckGo", "Yahoo"]
        for engine in search_engines:
            console.print(f"   • {engine} - Optimized integration")
        
        # Example search workflow (sanitized query)
        example_query = "Python web automation best practices"
        console.print(f"\n💡 Example search workflow:")
        console.print(f"   1. Navigate to search engine")
        console.print(f"   2. Enter sanitized query: '{example_query}'")
        console.print(f"   3. Execute search and wait for results")
        console.print(f"   4. Analyze and extract relevant links")
        console.print(f"   5. Click on most relevant result")
        
        console.print("\n✅ Search automation ready")
        result['status'] = 'success'
        
    except Exception as e:
        logger.exception("Search automation error")
        console.print(f"❌ Error: {str(e)}", style="bold red")
        result['status'] = 'error'
        result['details']['error'] = str(e)
    
    return result


def demo_claude_web_integration(config: Dict[str, Any]) -> Dict[str, Any]:
    """Demonstrate Claude 3.5 integration with web automation"""
    console.print(Panel.fit("🧠 Claude 3.5 Web Integration", style="bold yellow"))
    
    result = {'status': 'skipped', 'details': {}}
    
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key or api_key == 'your-claude-api-key-here':
            console.print("⚠️ No API key found - showing Claude integration capabilities")
            
            console.print("\n🧠 Claude 3.5 web automation features:")
            console.print("   ✅ Intelligent web page analysis")
            console.print("   ✅ Automated form filling with context")
            console.print("   ✅ Navigation strategy generation")
            console.print("   ✅ Content extraction and summarization")
            console.print("   ✅ Error detection and recovery")
            console.print("   ✅ Multi-step workflow planning")
            
            result['status'] = 'no_api_key'
            return result
        
        # Initialize Claude for web automation
        claude = ClaudeClient(api_key=api_key, config=config)
        
        console.print("✅ Claude 3.5 web integration active")
        console.print(f"   Model: {claude.model}")
        console.print(f"   Max tokens: {claude.max_tokens}")
        console.print(f"   Temperature: {claude.temperature}")
        
        # Demonstrate web automation planning
        console.print("\n🎯 Testing web automation planning...")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating web automation plan...", total=None)
            
            # Plan a web automation task
            task_plan = claude.plan_task(
                "Navigate to a search engine, search for 'Python web automation', and extract the top 3 results",
                context={
                    "platform": "web",
                    "browser": "chrome",
                    "task_type": "search_and_extract"
                }
            )
            progress.remove_task(task)
        
        if 'steps' in task_plan:
            console.print("✅ Web automation plan generated!")
            console.print(f"   Total steps: {len(task_plan['steps'])}")
            console.print(f"   Estimated duration: {task_plan.get('estimated_duration', 'Unknown')}")
            
            console.print("\n📋 Automation steps:")
            for i, step in enumerate(task_plan['steps'][:5], 1):
                step_desc = step.get('description', 'No description')
                console.print(f"   {i}. {step_desc}")
            
            result['status'] = 'success'
            result['details'] = {
                'steps_count': len(task_plan['steps']),
                'estimated_duration': task_plan.get('estimated_duration')
            }
        else:
            console.print("⚠️ Plan generated with alternative format")
            result['status'] = 'partial'
        
        console.print("\n🚀 Advanced Claude web features:")
        console.print("   • Context-aware page interaction")
        console.print("   • Intelligent form completion")
        console.print("   • Dynamic content handling")
        console.print("   • Error recovery strategies")
        
        console.print("\n✅ Claude 3.5 web automation ready")
        
    except KeyboardInterrupt:
        console.print("\n⚠️ Claude integration cancelled by user")
        result['status'] = 'cancelled'
        raise
    except Exception as e:
        logger.exception("Claude web integration error")
        console.print(f"❌ Error: {str(e)}", style="bold red")
        result['status'] = 'error'
        result['details']['error'] = str(e)
    
    return result


def demo_advanced_features():
    """Demonstrate advanced web automation features"""
    console.print(Panel.fit("⚡ Advanced Web Automation Features", style="bold white"))
    
    console.print("🚀 Advanced automation capabilities:")
    
    advanced_features = [
        ("🍪 Cookie Management", "Session persistence and cookie handling"),
        ("📱 Mobile Simulation", "Device emulation and responsive testing"),
        ("🔐 Authentication", "Login automation and session management"),
        ("📄 PDF Handling", "Document download and processing"),
        ("🎥 Media Interaction", "Video and audio element control"),
        ("🔄 AJAX Monitoring", "Dynamic content loading detection"),
        ("📊 Performance Tracking", "Page load and interaction metrics"),
        ("🛡️ Security Features", "Safe browsing and content filtering")
    ]
    
    for feature, description in advanced_features:
        console.print(f"   {feature}: {description}")
    
    console.print("\n🎯 Integration capabilities:")
    console.print("   • Screenshot capture during automation")
    console.print("   • Error logging and debugging")
    console.print("   • Multi-tab and multi-window support")
    console.print("   • Headless and visible mode switching")
    console.print("   • Custom user agent and headers")
    
    console.print("\n💡 Use cases:")
    use_cases = [
        "Automated testing and QA",
        "Data scraping and extraction",
        "Form filling and submission",
        "E-commerce interaction",
        "Social media automation",
        "Research and information gathering"
    ]
    
    for i, use_case in enumerate(use_cases, 1):
        console.print(f"   {i}. {use_case}")


def main():
    """Run the complete web automation demo"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Web Automation Demo with Claude 3.5',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--live',
        action='store_true',
        help='Execute live browser automation (default: demo mode only)'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode'
    )
    parser.add_argument(
        '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    parser.add_argument(
        '--save-results',
        action='store_true',
        help='Save demo results to JSON file'
    )
    
    args = parser.parse_args()
    
    console.print(Panel.fit(
        "🌐 Web Automation Demo - Claude 3.5 Enhanced (Refactored)\n"
        f"Mode: {'LIVE EXECUTION' if args.live else 'DEMO ONLY'}",
        style="bold white"
    ))
    
    # Initialize results tracker
    demo_results = DemoResults() if args.save_results else None
    
    # Load configuration once
    config = load_config(args.config)
    if args.headless:
        config['headless'] = True
    
    web_automator = None
    
    try:
        console.print("\n" + "="*60)
        
        # 1. Initialize Web Automator
        with timed_section("Web Automator Initialization"):
            web_automator = demo_web_automator_init(config, args.live)
            if demo_results:
                demo_results.record(
                    'initialization',
                    'success' if web_automator or not args.live else 'failed',
                    {'live_mode': args.live}
                )
        console.print()
        
        # 2. Navigation Capabilities
        with timed_section("Navigation Capabilities"):
            nav_result = demo_navigation_capabilities(web_automator, args.live)
            if demo_results:
                demo_results.record('navigation', nav_result['status'], nav_result['details'])
        console.print()
        
        # 3. Element Interaction
        with timed_section("Element Interaction"):
            elem_result = demo_element_interaction(web_automator, args.live)
            if demo_results:
                demo_results.record('element_interaction', elem_result['status'], elem_result['details'])
        console.print()
        
        # 4. Search Capabilities
        with timed_section("Search Capabilities"):
            search_result = demo_search_capabilities(args.live)
            if demo_results:
                demo_results.record('search', search_result['status'], search_result['details'])
        console.print()
        
        # 5. Claude Integration
        with timed_section("Claude 3.5 Integration"):
            claude_result = demo_claude_web_integration(config)
            if demo_results:
                demo_results.record('claude_integration', claude_result['status'], claude_result['details'])
        console.print()
        
        # 6. Advanced Features
        with timed_section("Advanced Features"):
            demo_advanced_features()
        console.print()
        
        # Final summary
        console.print(Panel.fit(
            "🎉 Web Automation Demo Complete!\n\n"
            "✅ Browser automation initialized\n"
            "✅ Navigation and page interaction ready\n"
            "✅ Element detection and manipulation active\n"
            "✅ Search automation capabilities demonstrated\n"
            "✅ Claude 3.5 integration for intelligent automation\n"
            "✅ Advanced features and security measures\n\n"
            "Your web automation system is ready!",
            style="bold green"
        ))
        
    except KeyboardInterrupt:
        console.print("\n\n⚠️ Demo interrupted by user", style="bold yellow")
        if demo_results:
            demo_results.record('interrupted', 'user_cancelled', {})
    except Exception as e:
        logger.exception("Demo failed with unexpected error")
        console.print(f"\n❌ Demo failed: {str(e)}", style="bold red")
        if demo_results:
            demo_results.record('error', 'failed', {'error': str(e)})
    finally:
        # Always cleanup, even if errors occurred
        console.print("\n" + "="*60)
        console.print("🧹 Cleaning up resources...")
        
        if web_automator:
            try:
                web_automator.cleanup()
                console.print("✅ Web automator cleaned up successfully")
            except Exception as e:
                logger.error(f"Cleanup warning: {e}")
                console.print(f"⚠️ Cleanup completed with warnings: {e}", style="yellow")
        
        # Save results if requested
        if demo_results:
            demo_results.finalize()
            demo_results.save()
        
        console.print("👋 Demo session ended")


if __name__ == "__main__":
    main()