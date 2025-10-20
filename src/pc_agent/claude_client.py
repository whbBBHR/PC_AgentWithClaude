"""
Claude Client - Interface for Claude Sonnet 4.5 API integration
Enhanced with the latest Claude Sonnet 4.5 model (claude-sonnet-4-5-20250929) 
for superior task planning, vision analysis, and automation guidance.
"""

import anthropic
import json
import base64
import os
from typing import Dict, List, Optional, Any
from loguru import logger

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


class ClaudeClient:
    """Client for interacting with Claude API"""
    
    def __init__(self, api_key: str = None, config: Dict[str, Any] = None):
        """Initialize Claude client with enhanced configuration"""
        # Try to get API key from parameter, environment, or config
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = None
        
        # Load configuration with Claude Sonnet 4.5 model defaults
        # Using claude-sonnet-4-5-20250929 - Latest Claude Sonnet 4.5 model
        self.config = config or {}
        self.model = self.config.get('claude_model', 'claude-sonnet-4-5-20250929')  # Claude Sonnet 4.5 for text tasks
        self.vision_model = self.config.get('vision_model', 'claude-sonnet-4-5-20250929')  # Claude Sonnet 4.5 with vision capabilities
        self.max_tokens = self.config.get('max_tokens', 8192)
        self.temperature = self.config.get('temperature', 0.1)
        
        if self.api_key and self.api_key != 'your-claude-api-key-here':
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info(f"Claude client initialized successfully with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize Claude client: {e}")
        else:
            logger.warning("No API key provided for Claude client")

    def analyze_screenshot(self, image_data: bytes, task_description: str = "") -> Dict[str, Any]:
        """
        Analyze screenshot using Claude's vision capabilities
        
        Args:
            image_data: Screenshot image data
            task_description: Optional task context
            
        Returns:
            Analysis results from Claude
        """
        if not self.client:
            return {"error": "Claude client not initialized"}
            
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            prompt = f"""Analyze this screenshot and identify interactive elements.
            
            Task context: {task_description}
            
            Please identify:
            1. Clickable buttons and their purposes
            2. Text input fields
            3. Links and navigation elements
            4. Any forms or interactive areas
            5. The current state of the interface
            6. Recommended next actions
            
            Return your analysis in JSON format with the following structure:
            {{
                "elements": [
                    {{
                        "type": "button|link|input|form",
                        "text": "visible text",
                        "purpose": "what this element does",
                        "location": "approximate location description"
                    }}
                ],
                "current_state": "description of current screen state",
                "recommended_actions": ["list of suggested next steps"],
                "confidence": 0.8
            }}"""
            
            message = self.client.messages.create(
                model=self.vision_model,
                max_tokens=min(self.max_tokens, 4096),
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            response_text = message.content[0].text
            
            # Try to parse JSON response
            try:
                analysis = json.loads(response_text)
                return analysis
            except json.JSONDecodeError:
                # If not valid JSON, return the raw response
                return {
                    "raw_response": response_text,
                    "error": "Could not parse JSON response"
                }
                
        except Exception as e:
            logger.error(f"Failed to analyze screenshot with Claude: {e}")
            return {"error": str(e)}

    def plan_task(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a task execution plan using Claude
        
        Args:
            task_description: Natural language task description
            context: Optional context information
            
        Returns:
            Task execution plan
        """
        if not self.client:
            return {"error": "Claude client not initialized"}
            
        try:
            context_str = json.dumps(context, indent=2) if context else "No additional context provided"
            
            prompt = f"""Create a detailed execution plan for this computer automation task:

Task: {task_description}

Context: {context_str}

Please create a step-by-step plan that can be executed by a computer automation system. 
The system has these capabilities:
- Screen capture and analysis
- Mouse clicking at coordinates
- Keyboard input and key combinations
- Web browser automation
- Element detection and interaction

Return your plan in JSON format:
{{
    "task": "original task description",
    "steps": [
        {{
            "step_number": 1,
            "action": "click|type|navigate|wait|analyze",
            "description": "what to do in this step",
            "parameters": {{
                "target": "what element to interact with",
                "value": "text to type or coordinates",
                "timeout": 10
            }},
            "success_criteria": "how to verify this step succeeded"
        }}
    ],
    "estimated_duration": "2-3 minutes",
    "prerequisites": ["any requirements before starting"],
    "potential_issues": ["possible problems and solutions"]
}}"""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=min(self.max_tokens, 4096),
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = message.content[0].text
            
            try:
                plan = json.loads(response_text)
                logger.info(f"Task plan created with {len(plan.get('steps', []))} steps")
                return plan
            except json.JSONDecodeError:
                return {
                    "raw_response": response_text,
                    "error": "Could not parse JSON response"
                }
                
        except Exception as e:
            logger.error(f"Failed to create task plan: {e}")
            return {"error": str(e)}

    def decide_next_action(self, current_state: str, goal: str, 
                          available_actions: List[str]) -> Dict[str, Any]:
        """
        Get Claude's recommendation for the next action
        
        Args:
            current_state: Description of current screen/state
            goal: The target goal
            available_actions: List of possible actions
            
        Returns:
            Recommended action and reasoning
        """
        if not self.client:
            return {"error": "Claude client not initialized"}
            
        try:
            prompt = f"""Given the current state and goal, recommend the best next action.

Current State: {current_state}

Goal: {goal}

Available Actions: {', '.join(available_actions)}

Please analyze the situation and recommend the best next action. Consider:
- Progress toward the goal
- Efficiency of different approaches
- Potential risks or issues
- Alternative strategies

Return your recommendation in JSON format:
{{
    "recommended_action": "specific action to take",
    "reasoning": "why this action is best",
    "confidence": 0.9,
    "alternative_actions": ["other possible actions"],
    "warnings": ["any potential issues to watch for"]
}}"""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=min(self.max_tokens // 2, 2048),
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = message.content[0].text
            
            try:
                decision = json.loads(response_text)
                return decision
            except json.JSONDecodeError:
                return {
                    "raw_response": response_text,
                    "error": "Could not parse JSON response"
                }
                
        except Exception as e:
            logger.error(f"Failed to get action recommendation: {e}")
            return {"error": str(e)}

    def interpret_ui_element(self, element_description: str, 
                           context: str = "") -> Dict[str, Any]:
        """
        Get Claude's interpretation of a UI element
        
        Args:
            element_description: Description of the UI element
            context: Additional context about the interface
            
        Returns:
            Element interpretation and interaction recommendations
        """
        if not self.client:
            return {"error": "Claude client not initialized"}
            
        try:
            prompt = f"""Analyze this UI element and provide interaction guidance:

Element: {element_description}
Context: {context}

Please provide:
1. What type of UI element this is
2. Its likely purpose/function
3. How to interact with it
4. What might happen when interacted with
5. Any precautions or considerations

Return as JSON:
{{
    "element_type": "button|input|link|menu|etc",
    "purpose": "what this element does",
    "interaction_method": "how to interact with it",
    "expected_result": "what should happen",
    "confidence": 0.8,
    "precautions": ["any warnings or considerations"]
}}"""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=min(self.max_tokens // 4, 1024),
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = message.content[0].text
            
            try:
                interpretation = json.loads(response_text)
                return interpretation
            except json.JSONDecodeError:
                return {
                    "raw_response": response_text,
                    "error": "Could not parse JSON response"
                }
                
        except Exception as e:
            logger.error(f"Failed to interpret UI element: {e}")
            return {"error": str(e)}

    def generate_response(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate a general response from Claude
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum response length
            
        Returns:
            Claude's response text
        """
        if not self.client:
            return "Error: Claude client not initialized"
            
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=min(max_tokens, self.max_tokens),
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return f"Error: {str(e)}"

    def is_available(self) -> bool:
        """Check if Claude client is available and working"""
        return self.client is not None

    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Claude API"""
        if not self.client:
            return {
                "status": "error",
                "message": "Client not initialized"
            }
            
        try:
            # Simple test message
            response = self.generate_response("Hello, respond with 'OK' if you can hear me.")
            
            if "OK" in response or "ok" in response.lower():
                return {
                    "status": "success",
                    "message": "Connection successful"
                }
            else:
                return {
                    "status": "warning",
                    "message": "Unexpected response",
                    "response": response
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }