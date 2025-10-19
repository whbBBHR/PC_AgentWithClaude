"""
Web Automator - Web browsing and automation capabilities
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import time
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus
from loguru import logger


class WebAutomator:
    """Web automation using Selenium WebDriver"""
    
    def __init__(self, config):
        """Initialize web automator"""
        self.config = config
        self.driver = None
        self.wait = None
        
    def _setup_driver(self):
        """Setup WebDriver based on configuration"""
        if self.driver is not None:
            return self.driver
            
        try:
            browser = self.config.browser.lower()
            
            if browser == "chrome":
                options = ChromeOptions()
                if self.config.headless:
                    options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                
                self.driver = webdriver.Chrome(options=options)
                
            elif browser == "firefox":
                options = FirefoxOptions()
                if self.config.headless:
                    options.add_argument("--headless")
                    
                self.driver = webdriver.Firefox(options=options)
                
            else:
                logger.error(f"Unsupported browser: {browser}")
                return None
                
            # Setup wait
            self.wait = WebDriverWait(self.driver, self.config.wait_timeout)
            
            # Set window size
            self.driver.set_window_size(1920, 1080)
            
            logger.info(f"WebDriver initialized: {browser}")
            return self.driver
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {e}")
            return None

    def navigate_to(self, url: str) -> bool:
        """
        Navigate to a URL
        
        Args:
            url: URL to navigate to
            
        Returns:
            True if successful
        """
        try:
            if not self._setup_driver():
                return False
                
            logger.debug(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False

    def search(self, query: str, engine: str = "google") -> bool:
        """
        Perform web search
        
        Args:
            query: Search query
            engine: Search engine ('google', 'bing', 'duckduckgo')
            
        Returns:
            True if successful
        """
        try:
            search_urls = {
                "google": f"https://www.google.com/search?q={quote_plus(query)}",
                "bing": f"https://www.bing.com/search?q={quote_plus(query)}",
                "duckduckgo": f"https://duckduckgo.com/?q={quote_plus(query)}"
            }
            
            if engine not in search_urls:
                logger.error(f"Unsupported search engine: {engine}")
                return False
                
            url = search_urls[engine]
            logger.info(f"Searching for '{query}' on {engine}")
            
            return self.navigate_to(url)
            
        except Exception as e:
            logger.error(f"Failed to search for '{query}': {e}")
            return False

    def find_element(self, selector: str, by: By = By.CSS_SELECTOR, 
                    timeout: Optional[int] = None) -> Optional[Any]:
        """
        Find element on page
        
        Args:
            selector: Element selector
            by: Selection method (By.ID, By.CLASS_NAME, etc.)
            timeout: Wait timeout
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            if not self.driver:
                return None
                
            if timeout is None:
                timeout = self.config.wait_timeout
                
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, selector)))
            
            return element
            
        except TimeoutException:
            logger.debug(f"Element not found: {selector}")
            return None
        except Exception as e:
            logger.error(f"Error finding element {selector}: {e}")
            return None

    def find_elements(self, selector: str, by: By = By.CSS_SELECTOR) -> List[Any]:
        """
        Find multiple elements on page
        
        Args:
            selector: Element selector
            by: Selection method
            
        Returns:
            List of WebElements
        """
        try:
            if not self.driver:
                return []
                
            elements = self.driver.find_elements(by, selector)
            return elements
            
        except Exception as e:
            logger.error(f"Error finding elements {selector}: {e}")
            return []

    def click_element(self, selector: str, by: By = By.CSS_SELECTOR) -> bool:
        """
        Click an element
        
        Args:
            selector: Element selector
            by: Selection method
            
        Returns:
            True if successful
        """
        try:
            element = self.find_element(selector, by)
            if element:
                # Wait for element to be clickable
                self.wait.until(EC.element_to_be_clickable((by, selector)))
                element.click()
                logger.debug(f"Clicked element: {selector}")
                return True
            else:
                logger.warning(f"Element not found for clicking: {selector}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to click element {selector}: {e}")
            return False

    def click_element_by_text(self, text: str) -> bool:
        """
        Click element containing specific text
        
        Args:
            text: Text to search for
            
        Returns:
            True if successful
        """
        try:
            # Try different element types that might contain clickable text
            selectors = [
                f"//button[contains(text(), '{text}')]",
                f"//a[contains(text(), '{text}')]",
                f"//span[contains(text(), '{text}')]",
                f"//div[contains(text(), '{text}')]",
                f"//*[contains(text(), '{text}')]"
            ]
            
            for selector in selectors:
                try:
                    element = self.find_element(selector, By.XPATH)
                    if element and element.is_displayed():
                        element.click()
                        logger.debug(f"Clicked element with text: {text}")
                        return True
                except:
                    continue
                    
            logger.warning(f"No clickable element found with text: {text}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to click element with text '{text}': {e}")
            return False

    def type_in_element(self, selector: str, text: str, 
                       by: By = By.CSS_SELECTOR, clear_first: bool = True) -> bool:
        """
        Type text in an element
        
        Args:
            selector: Element selector
            text: Text to type
            by: Selection method
            clear_first: Whether to clear existing text first
            
        Returns:
            True if successful
        """
        try:
            element = self.find_element(selector, by)
            if element:
                if clear_first:
                    element.clear()
                    
                element.send_keys(text)
                logger.debug(f"Typed text in {selector}: {text[:50]}...")
                return True
            else:
                logger.warning(f"Element not found for typing: {selector}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to type in element {selector}: {e}")
            return False

    def fill_form(self, form_data: Dict[str, str]) -> bool:
        """
        Fill form fields
        
        Args:
            form_data: Dictionary of field_name: value pairs
            
        Returns:
            True if all fields filled successfully
        """
        try:
            success_count = 0
            
            for field_name, value in form_data.items():
                # Try different ways to find the form field
                selectors = [
                    f"input[name='{field_name}']",
                    f"input[id='{field_name}']",
                    f"textarea[name='{field_name}']",
                    f"textarea[id='{field_name}']",
                    f"select[name='{field_name}']",
                    f"select[id='{field_name}']"
                ]
                
                filled = False
                for selector in selectors:
                    if self.type_in_element(selector, value):
                        success_count += 1
                        filled = True
                        break
                        
                if not filled:
                    logger.warning(f"Could not fill field: {field_name}")
            
            return success_count == len(form_data)
            
        except Exception as e:
            logger.error(f"Failed to fill form: {e}")
            return False

    def submit_form(self, form_selector: str = "form") -> bool:
        """
        Submit a form
        
        Args:
            form_selector: Form element selector
            
        Returns:
            True if successful
        """
        try:
            # Try to find submit button first
            submit_buttons = [
                "input[type='submit']",
                "button[type='submit']",
                "button:contains('Submit')",
                "button:contains('Sign in')",
                "button:contains('Login')",
                "button:contains('Search')"
            ]
            
            for selector in submit_buttons:
                if self.click_element(selector):
                    logger.debug("Form submitted via submit button")
                    return True
            
            # If no submit button found, try pressing Enter on form
            form = self.find_element(form_selector)
            if form:
                form.send_keys(Keys.RETURN)
                logger.debug("Form submitted via Enter key")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to submit form: {e}")
            return False

    def scroll_page(self, direction: str, amount: int = 3) -> bool:
        """
        Scroll the page
        
        Args:
            direction: 'up' or 'down'
            amount: Number of scroll units
            
        Returns:
            True if successful
        """
        try:
            if not self.driver:
                return False
                
            if direction.lower() == 'down':
                for _ in range(amount):
                    self.driver.execute_script("window.scrollBy(0, 300);")
                    time.sleep(0.2)
            elif direction.lower() == 'up':
                for _ in range(amount):
                    self.driver.execute_script("window.scrollBy(0, -300);")
                    time.sleep(0.2)
            else:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to scroll {direction}: {e}")
            return False

    def get_page_title(self) -> str:
        """Get current page title"""
        try:
            return self.driver.title if self.driver else ""
        except Exception as e:
            logger.error(f"Failed to get page title: {e}")
            return ""

    def get_current_url(self) -> str:
        """Get current URL"""
        try:
            return self.driver.current_url if self.driver else ""
        except Exception as e:
            logger.error(f"Failed to get current URL: {e}")
            return ""

    def get_page_source(self) -> str:
        """Get page HTML source"""
        try:
            return self.driver.page_source if self.driver else ""
        except Exception as e:
            logger.error(f"Failed to get page source: {e}")
            return ""

    def take_screenshot(self, filename: str) -> bool:
        """
        Take screenshot of current page
        
        Args:
            filename: Path to save screenshot
            
        Returns:
            True if successful
        """
        try:
            if not self.driver:
                return False
                
            self.driver.save_screenshot(filename)
            logger.debug(f"Screenshot saved: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False

    def wait_for_element_visible(self, selector: str, by: By = By.CSS_SELECTOR, 
                               timeout: Optional[int] = None) -> bool:
        """
        Wait for element to become visible
        
        Args:
            selector: Element selector
            by: Selection method
            timeout: Wait timeout
            
        Returns:
            True if element becomes visible
        """
        try:
            if timeout is None:
                timeout = self.config.wait_timeout
                
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located((by, selector)))
            return True
            
        except TimeoutException:
            logger.debug(f"Element not visible within timeout: {selector}")
            return False
        except Exception as e:
            logger.error(f"Error waiting for element visibility: {e}")
            return False

    def execute_javascript(self, script: str) -> Any:
        """
        Execute JavaScript on the page
        
        Args:
            script: JavaScript code to execute
            
        Returns:
            Result of JavaScript execution
        """
        try:
            if not self.driver:
                return None
                
            result = self.driver.execute_script(script)
            logger.debug(f"Executed JavaScript: {script[:100]}...")
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute JavaScript: {e}")
            return None

    def cleanup(self):
        """Close browser and cleanup resources"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info("WebDriver cleaned up")
        except Exception as e:
            logger.error(f"Error during WebDriver cleanup: {e}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()