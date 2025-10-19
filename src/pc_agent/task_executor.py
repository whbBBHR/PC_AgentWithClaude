"""
Task Executor - Orchestrates complex multi-step computer tasks
"""

import time
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from loguru import logger


class TaskStep:
    """Represents a single step in a task execution plan"""
    
    def __init__(self, step_data: Dict[str, Any]):
        self.step_number = step_data.get('step_number', 0)
        self.action = step_data.get('action', '')
        self.description = step_data.get('description', '')
        self.parameters = step_data.get('parameters', {})
        self.success_criteria = step_data.get('success_criteria', '')
        self.timeout = step_data.get('timeout', 30)
        self.retries = step_data.get('retries', 2)
        
        # Execution tracking
        self.status = 'pending'  # pending, running, completed, failed, skipped
        self.start_time = None
        self.end_time = None
        self.error_message = None
        self.result = None
        self.attempts = 0

    def start(self):
        """Mark step as started"""
        self.status = 'running'
        self.start_time = datetime.now()
        self.attempts += 1

    def complete(self, result: Any = None):
        """Mark step as completed"""
        self.status = 'completed'
        self.end_time = datetime.now()
        self.result = result

    def fail(self, error: str):
        """Mark step as failed"""
        self.status = 'failed'
        self.end_time = datetime.now()
        self.error_message = error

    def skip(self, reason: str):
        """Mark step as skipped"""
        self.status = 'skipped'
        self.end_time = datetime.now()
        self.error_message = reason

    @property
    def duration(self) -> Optional[timedelta]:
        """Get step execution duration"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary"""
        return {
            'step_number': self.step_number,
            'action': self.action,
            'description': self.description,
            'parameters': self.parameters,
            'success_criteria': self.success_criteria,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration.total_seconds() if self.duration else None,
            'attempts': self.attempts,
            'error_message': self.error_message,
            'result': self.result
        }


class TaskExecutor:
    """Executes complex multi-step computer automation tasks"""
    
    def __init__(self, config):
        """Initialize task executor"""
        self.config = config
        
        # Will be set by the ComputerAgent
        self.computer_agent = None
        self.claude_client = None
        self.vision_analyzer = None
        self.web_automator = None
        
        # Task execution state
        self.current_task = None
        self.execution_log = []

    def set_components(self, computer_agent, claude_client, vision_analyzer, web_automator):
        """Set component references"""
        self.computer_agent = computer_agent
        self.claude_client = claude_client
        self.vision_analyzer = vision_analyzer
        self.web_automator = web_automator

    def execute(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a natural language task
        
        Args:
            task_description: Description of task to perform
            context: Optional context information
            
        Returns:
            Execution results
        """
        try:
            logger.info(f"Starting task execution: {task_description}")
            
            # Create execution plan using Claude
            plan = self._create_execution_plan(task_description, context)
            
            if 'error' in plan:
                return {
                    'status': 'failed',
                    'error': 'Failed to create execution plan',
                    'details': plan
                }
            
            # Execute the plan
            result = self._execute_plan(plan, task_description)
            
            return result
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'task': task_description
            }

    def _create_execution_plan(self, task_description: str, 
                             context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create execution plan using Claude"""
        if not self.claude_client or not self.claude_client.is_available():
            # Fallback to basic plan creation
            return self._create_basic_plan(task_description)
        
        try:
            # Get current screen context
            if self.computer_agent:
                screenshot = self.computer_agent.capture_screen()
                screen_analysis = self.vision_analyzer.analyze_image(screenshot)
                
                if context is None:
                    context = {}
                context['current_screen'] = screen_analysis
            
            # Use Claude to create plan
            plan = self.claude_client.plan_task(task_description, context)
            
            return plan
            
        except Exception as e:
            logger.error(f"Failed to create plan with Claude: {e}")
            return self._create_basic_plan(task_description)

    def _create_basic_plan(self, task_description: str) -> Dict[str, Any]:
        """Create a basic execution plan without AI assistance"""
        logger.info("Creating basic execution plan")
        
        # Simple heuristic-based plan creation
        steps = []
        
        task_lower = task_description.lower()
        
        if 'search' in task_lower and 'google' in task_lower:
            steps = [
                {
                    'step_number': 1,
                    'action': 'navigate',
                    'description': 'Open Google search',
                    'parameters': {'url': 'https://www.google.com'},
                    'success_criteria': 'Google homepage loaded'
                },
                {
                    'step_number': 2,
                    'action': 'type',
                    'description': 'Enter search query',
                    'parameters': {'selector': 'input[name="q"]', 'text': 'search query'},
                    'success_criteria': 'Text entered in search box'
                },
                {
                    'step_number': 3,
                    'action': 'click',
                    'description': 'Click search button or press Enter',
                    'parameters': {'key': 'enter'},
                    'success_criteria': 'Search results displayed'
                }
            ]
        else:
            # Generic plan - analyze screen and ask Claude for guidance
            steps = [
                {
                    'step_number': 1,
                    'action': 'analyze',
                    'description': 'Analyze current screen state',
                    'parameters': {},
                    'success_criteria': 'Screen analysis completed'
                },
                {
                    'step_number': 2,
                    'action': 'decide',
                    'description': 'Determine best approach based on analysis',
                    'parameters': {'task': task_description},
                    'success_criteria': 'Action plan determined'
                }
            ]
        
        return {
            'task': task_description,
            'steps': steps,
            'estimated_duration': '1-2 minutes',
            'prerequisites': [],
            'potential_issues': ['Screen layout may differ from expected']
        }

    def _execute_plan(self, plan: Dict[str, Any], original_task: str) -> Dict[str, Any]:
        """Execute a task plan"""
        steps_data = plan.get('steps', [])
        task_steps = [TaskStep(step_data) for step_data in steps_data]
        
        start_time = datetime.now()
        completed_steps = 0
        failed_steps = 0
        
        execution_log = {
            'task': original_task,
            'plan': plan,
            'start_time': start_time.isoformat(),
            'steps': [],
            'status': 'running'
        }
        
        try:
            for step in task_steps:
                logger.info(f"Executing step {step.step_number}: {step.description}")
                
                # Execute step with retries
                success = self._execute_step_with_retries(step)
                
                execution_log['steps'].append(step.to_dict())
                
                if success:
                    completed_steps += 1
                    logger.info(f"Step {step.step_number} completed successfully")
                else:
                    failed_steps += 1
                    logger.error(f"Step {step.step_number} failed: {step.error_message}")
                    
                    # Decide whether to continue or abort
                    if self._should_abort_on_failure(step, task_steps):
                        logger.warning("Aborting task execution due to critical step failure")
                        break
                
                # Small delay between steps
                time.sleep(0.5)
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            # Determine overall status
            if failed_steps == 0:
                status = 'completed'
            elif completed_steps > 0:
                status = 'partially_completed'
            else:
                status = 'failed'
            
            execution_log.update({
                'end_time': end_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'status': status,
                'completed_steps': completed_steps,
                'failed_steps': failed_steps,
                'total_steps': len(task_steps)
            })
            
            return execution_log
            
        except Exception as e:
            logger.error(f"Plan execution failed: {e}")
            execution_log.update({
                'status': 'error',
                'error': str(e),
                'end_time': datetime.now().isoformat()
            })
            return execution_log

    def _execute_step_with_retries(self, step: TaskStep) -> bool:
        """Execute a single step with retry logic"""
        for attempt in range(step.retries + 1):
            try:
                step.start()
                
                success = self._execute_single_step(step)
                
                if success:
                    step.complete()
                    return True
                else:
                    if attempt < step.retries:
                        logger.warning(f"Step {step.step_number} failed, retrying...")
                        time.sleep(1)
                        continue
                    else:
                        step.fail("Max retries exceeded")
                        return False
                        
            except Exception as e:
                error_msg = f"Step execution error: {str(e)}"
                logger.error(error_msg)
                
                if attempt < step.retries:
                    logger.warning(f"Retrying step {step.step_number} due to error")
                    time.sleep(1)
                    continue
                else:
                    step.fail(error_msg)
                    return False
        
        return False

    def _execute_single_step(self, step: TaskStep) -> bool:
        """Execute a single step action"""
        action = step.action.lower()
        params = step.parameters
        
        try:
            if action == 'click':
                return self._execute_click_action(params)
            elif action == 'type':
                return self._execute_type_action(params)
            elif action == 'navigate':
                return self._execute_navigate_action(params)
            elif action == 'wait':
                return self._execute_wait_action(params)
            elif action == 'analyze':
                return self._execute_analyze_action(params)
            elif action == 'decide':
                return self._execute_decide_action(params)
            elif action == 'scroll':
                return self._execute_scroll_action(params)
            elif action == 'key':
                return self._execute_key_action(params)
            else:
                logger.error(f"Unknown action: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing {action} action: {e}")
            return False

    def _execute_click_action(self, params: Dict[str, Any]) -> bool:
        """Execute click action"""
        if 'coordinates' in params:
            x, y = params['coordinates']
            return self.computer_agent.click_at(x, y)
        elif 'selector' in params:
            return self.web_automator.click_element(params['selector'])
        elif 'text' in params:
            return self.web_automator.click_element_by_text(params['text'])
        elif 'template' in params:
            return self.computer_agent.click_element(params['template'])
        else:
            logger.error("Click action missing target specification")
            return False

    def _execute_type_action(self, params: Dict[str, Any]) -> bool:
        """Execute type action"""
        text = params.get('text', '')
        
        if 'selector' in params:
            return self.web_automator.type_in_element(params['selector'], text)
        else:
            return self.computer_agent.type_text(text)

    def _execute_navigate_action(self, params: Dict[str, Any]) -> bool:
        """Execute navigate action"""
        url = params.get('url', '')
        if url:
            return self.web_automator.navigate_to(url)
        return False

    def _execute_wait_action(self, params: Dict[str, Any]) -> bool:
        """Execute wait action"""
        duration = params.get('duration', 1.0)
        time.sleep(duration)
        return True

    def _execute_analyze_action(self, params: Dict[str, Any]) -> bool:
        """Execute screen analysis action"""
        try:
            screenshot = self.computer_agent.capture_screen()
            analysis = self.vision_analyzer.analyze_image(screenshot)
            # Store analysis result in step for later use
            return analysis is not None
        except Exception:
            return False

    def _execute_decide_action(self, params: Dict[str, Any]) -> bool:
        """Execute decision action using Claude"""
        if not self.claude_client or not self.claude_client.is_available():
            return True  # Skip if Claude not available
            
        try:
            task = params.get('task', '')
            # This would typically involve getting Claude's recommendation
            # and potentially modifying the execution plan
            return True
        except Exception:
            return False

    def _execute_scroll_action(self, params: Dict[str, Any]) -> bool:
        """Execute scroll action"""
        direction = params.get('direction', 'down')
        amount = params.get('amount', 3)
        
        if self.web_automator.driver:
            return self.web_automator.scroll_page(direction, amount)
        else:
            return self.computer_agent.scroll_page(direction, amount)

    def _execute_key_action(self, params: Dict[str, Any]) -> bool:
        """Execute key press action"""
        key = params.get('key', '')
        if key:
            return self.computer_agent.press_key(key)
        return False

    def _should_abort_on_failure(self, failed_step: TaskStep, 
                                remaining_steps: List[TaskStep]) -> bool:
        """Determine if task should be aborted due to step failure"""
        # Simple heuristic: abort if it's a navigation or critical setup step
        critical_actions = ['navigate', 'analyze']
        
        if failed_step.action.lower() in critical_actions:
            return True
            
        # Abort if too many consecutive failures
        recent_failures = 0
        for step in remaining_steps:
            if step.status == 'failed':
                recent_failures += 1
                if recent_failures >= 2:
                    return True
            else:
                break
                
        return False

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get history of task executions"""
        return self.execution_log.copy()

    def cancel_current_task(self) -> bool:
        """Cancel currently running task"""
        if self.current_task:
            logger.info("Cancelling current task execution")
            self.current_task = None
            return True
        return False