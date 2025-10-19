"""
PC Agent with Claude - Core Module
A computer-using agent that can interact with computer interfaces and perform automated tasks.
"""

from .computer_agent import ComputerAgent
from .vision_analyzer import VisionAnalyzer
from .web_automator import WebAutomator
from .task_executor import TaskExecutor
from .claude_client import ClaudeClient

__version__ = "1.0.0"
__all__ = [
    "ComputerAgent",
    "VisionAnalyzer", 
    "WebAutomator",
    "TaskExecutor",
    "ClaudeClient"
]