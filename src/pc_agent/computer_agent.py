"""
Computer Agent - Main class for computer interaction and automation
"""

import os
import time
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging
from pathlib import Path

# Screen and input handling
import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageDraw
from pynput import mouse, keyboard
import screeninfo

# Configuration and utilities
from loguru import logger
from pydantic import BaseModel

from .vision_analyzer import VisionAnalyzer
from .web_automator import WebAutomator
from .task_executor import TaskExecutor
from .claude_client import ClaudeClient


class AgentConfig(BaseModel):
    """Configuration for the Computer Agent"""
    anthropic_api_key: str = ""
    screenshot_path: str = "./screenshots"
    browser: str = "chrome"
    headless: bool = False
    wait_timeout: int = 10
    debug_mode: bool = True
    confidence_threshold: float = 0.8
    max_retries: int = 3


class ComputerAgent:
    """
    Main Computer Agent class that can interact with computer interfaces,
    perform web automation, and execute complex tasks using AI.
    """
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the Computer Agent"""
        self.config = self._load_config(config_path)
        self.setup_logging()
        
        # Initialize components
        self.vision_analyzer = VisionAnalyzer(self.config)
        self.web_automator = WebAutomator(self.config)
        self.task_executor = TaskExecutor(self.config)
        self.claude_client = ClaudeClient(
            api_key=self.config.anthropic_api_key,
            config=self.config.__dict__
        )
        
        # Set up component references for task executor
        self.task_executor.set_components(
            computer_agent=self,
            claude_client=self.claude_client,
            vision_analyzer=self.vision_analyzer,
            web_automator=self.web_automator
        )
        
        # Setup pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
        # Create screenshot directory
        Path(self.config.screenshot_path).mkdir(exist_ok=True)
        
        logger.info("Computer Agent initialized successfully")

    def _load_config(self, config_path: str) -> AgentConfig:
        """Load configuration from file or create default"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            return AgentConfig(**config_data)
        else:
            # Create default config
            config = AgentConfig()
            logger.warning(f"Config file {config_path} not found, using defaults")
            return config

    def setup_logging(self):
        """Setup logging configuration"""
        if self.config.debug_mode:
            logger.add("agent.log", rotation="10 MB", level="DEBUG")
        else:
            logger.add("agent.log", rotation="10 MB", level="INFO")

    # ===================
    # Screen Interaction Methods
    # ===================
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        Capture screenshot of the screen or specified region
        
        Args:
            region: (left, top, width, height) tuple for partial capture
            
        Returns:
            Screenshot as numpy array
        """
        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            
            # Convert to numpy array
            screenshot_np = np.array(screenshot)
            
            # Save screenshot if debug mode
            if self.config.debug_mode:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.join(
                    self.config.screenshot_path, 
                    f"screenshot_{timestamp}.png"
                )
                screenshot.save(screenshot_path)
                logger.debug(f"Screenshot saved: {screenshot_path}")
            
            return screenshot_np
            
        except Exception as e:
            logger.error(f"Failed to capture screen: {e}")
            raise

    def click_at(self, x: int, y: int, button: str = "left", clicks: int = 1) -> bool:
        """
        Click at specific coordinates
        
        Args:
            x, y: Coordinates to click
            button: Mouse button ('left', 'right', 'middle')
            clicks: Number of clicks (1 for single, 2 for double)
            
        Returns:
            True if successful
        """
        try:
            logger.debug(f"Clicking at ({x}, {y}) with {button} button")
            
            if clicks == 1:
                pyautogui.click(x, y, button=button)
            elif clicks == 2:
                pyautogui.doubleClick(x, y, button=button)
            else:
                for _ in range(clicks):
                    pyautogui.click(x, y, button=button)
                    time.sleep(0.1)
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to click at ({x}, {y}): {e}")
            return False

    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """
        Type text with specified interval between characters
        
        Args:
            text: Text to type
            interval: Delay between keystrokes
            
        Returns:
            True if successful
        """
        try:
            logger.debug(f"Typing text: {text[:50]}...")
            pyautogui.typewrite(text, interval=interval)
            return True
            
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            return False

    def press_key(self, key: str, presses: int = 1) -> bool:
        """
        Press keyboard key(s)
        
        Args:
            key: Key name (e.g., 'enter', 'ctrl+c', 'alt+tab')
            presses: Number of times to press
            
        Returns:
            True if successful
        """
        try:
            logger.debug(f"Pressing key: {key} ({presses} times)")
            
            if '+' in key:
                # Handle key combinations
                keys = key.split('+')
                pyautogui.hotkey(*keys)
            else:
                for _ in range(presses):
                    pyautogui.press(key)
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to press key {key}: {e}")
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
            logger.debug(f"Scrolling {direction} by {amount} units")
            
            if direction.lower() == 'up':
                pyautogui.scroll(amount)
            elif direction.lower() == 'down':
                pyautogui.scroll(-amount)
            else:
                logger.warning(f"Unknown scroll direction: {direction}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to scroll {direction}: {e}")
            return False

    def drag_to(self, start_x: int, start_y: int, end_x: int, end_y: int, 
                duration: float = 0.5) -> bool:
        """
        Drag from one point to another
        
        Args:
            start_x, start_y: Starting coordinates
            end_x, end_y: Ending coordinates  
            duration: Time to complete drag
            
        Returns:
            True if successful
        """
        try:
            logger.debug(f"Dragging from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            pyautogui.drag(end_x - start_x, end_y - start_y, 
                          duration=duration, button='left')
            return True
            
        except Exception as e:
            logger.error(f"Failed to drag: {e}")
            return False

    # ===================
    # Element Detection and Interaction
    # ===================
    
    def find_element_on_screen(self, template_path: str, 
                              confidence: Optional[float] = None) -> Optional[Tuple[int, int]]:
        """
        Find element on screen using template matching
        
        Args:
            template_path: Path to template image
            confidence: Confidence threshold (uses config default if None)
            
        Returns:
            (x, y) coordinates of element center, or None if not found
        """
        if confidence is None:
            confidence = self.config.confidence_threshold
            
        try:
            location = pyautogui.locateOnScreen(template_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                logger.debug(f"Found element at {center}")
                return (center.x, center.y)
            else:
                logger.debug(f"Element not found: {template_path}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to find element {template_path}: {e}")
            return None

    def click_element(self, template_path: str, confidence: Optional[float] = None, 
                     timeout: Optional[int] = None) -> bool:
        """
        Find and click an element on screen
        
        Args:
            template_path: Path to template image
            confidence: Confidence threshold
            timeout: Maximum time to wait for element
            
        Returns:
            True if element was found and clicked
        """
        if timeout is None:
            timeout = self.config.wait_timeout
            
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            location = self.find_element_on_screen(template_path, confidence)
            if location:
                return self.click_at(location[0], location[1])
            time.sleep(0.5)
            
        logger.warning(f"Element not found within timeout: {template_path}")
        return False

    def wait_for_element(self, template_path: str, timeout: Optional[int] = None) -> bool:
        """
        Wait for an element to appear on screen
        
        Args:
            template_path: Path to template image
            timeout: Maximum time to wait
            
        Returns:
            True if element appears within timeout
        """
        if timeout is None:
            timeout = self.config.wait_timeout
            
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.find_element_on_screen(template_path):
                return True
            time.sleep(0.5)
            
        return False

    # ===================
    # High-level Task Methods
    # ===================
    
    def execute_task(self, task_description: str) -> Dict[str, Any]:
        """
        Execute a natural language task using AI planning
        
        Args:
            task_description: Description of task to perform
            
        Returns:
            Dictionary with execution results
        """
        logger.info(f"Executing task: {task_description}")
        
        try:
            # Use task executor to plan and execute
            result = self.task_executor.execute(task_description)
            logger.info(f"Task completed: {result.get('status', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute task: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'task': task_description
            }

    def web_search(self, query: str, engine: str = "google") -> bool:
        """
        Perform web search
        
        Args:
            query: Search query
            engine: Search engine to use
            
        Returns:
            True if successful
        """
        return self.web_automator.search(query, engine)

    def navigate_to(self, url: str) -> bool:
        """
        Navigate to URL
        
        Args:
            url: URL to navigate to
            
        Returns:
            True if successful
        """
        return self.web_automator.navigate_to(url)

    def analyze_screen(self) -> Dict[str, Any]:
        """
        Analyze current screen content using computer vision
        
        Returns:
            Analysis results dictionary
        """
        screenshot = self.capture_screen()
        return self.vision_analyzer.analyze_image(screenshot)

    def get_screen_info(self) -> Dict[str, Any]:
        """
        Get information about available screens
        
        Returns:
            Dictionary with screen information
        """
        try:
            monitors = screeninfo.get_monitors()
            screen_info = {
                'primary': {
                    'width': pyautogui.size().width,
                    'height': pyautogui.size().height
                },
                'monitors': []
            }
            
            for monitor in monitors:
                screen_info['monitors'].append({
                    'x': monitor.x,
                    'y': monitor.y, 
                    'width': monitor.width,
                    'height': monitor.height,
                    'is_primary': monitor.is_primary
                })
                
            return screen_info
            
        except Exception as e:
            logger.error(f"Failed to get screen info: {e}")
            return {}

    def cleanup(self):
        """Cleanup resources"""
        try:
            self.web_automator.cleanup()
            logger.info("Computer Agent cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()