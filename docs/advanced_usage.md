# PC Agent with Claude - Advanced Computer Vision Guide

## Overview

This PC Agent integrates with **Claude Sonnet 3.5** to provide intelligent computer automation with advanced computer vision capabilities. The agent can understand screen content, plan complex tasks, and execute them autonomously.

## Key Features with Claude Sonnet 3.5

### 🧠 AI-Powered Decision Making
- **Task Planning**: Claude analyzes your natural language requests and creates step-by-step execution plans
- **Screen Understanding**: Uses Claude's vision capabilities to understand screen content and context
- **Adaptive Execution**: Adjusts behavior based on real-time screen analysis

### 👁️ Advanced Computer Vision
- **Element Detection**: Identifies buttons, text fields, links, and other UI elements
- **OCR Integration**: Extracts text from screenshots with high accuracy
- **Visual Analysis**: Analyzes screen layouts, colors, and visual patterns
- **Context Awareness**: Understands the relationship between different screen elements

### 🤖 Intelligent Automation
- **Web Automation**: Browse websites, fill forms, and interact with web applications
- **Desktop Interaction**: Click, type, scroll, and navigate desktop applications
- **Multi-Step Tasks**: Execute complex workflows with error handling and retries

## Configuration for Claude Sonnet 3.5

### API Setup

1. **Get your Claude API key** from Anthropic Console (https://console.anthropic.com/)

2. **Configure the agent**:
   ```json
   {
     "anthropic_api_key": "your-claude-api-key-here",
     "claude_model": "claude-3-5-sonnet-20241022",
     "vision_model": "claude-3-5-sonnet-20241022",
     "max_tokens": 4000,
     "screenshot_path": "./screenshots",
     "debug_mode": true
   }
   ```

### Model Selection

The agent is optimized for **Claude 3.5 Sonnet** which provides:
- **Superior vision capabilities** for screen analysis
- **Better reasoning** for complex task planning
- **Faster response times** compared to Claude 3 Opus
- **Cost-effective** for automation workloads

## Advanced Computer Vision Capabilities

### 1. Screen Analysis with Claude Vision

```python
from pc_agent import ComputerAgent

agent = ComputerAgent("config.json")

# Capture and analyze screen with Claude
screenshot = agent.capture_screen()

# Get Claude's interpretation
analysis = agent.claude_client.analyze_screenshot(
    screenshot_bytes, 
    "Find all clickable elements for web form submission"
)

# Claude returns structured analysis
if 'elements' in analysis:
    for element in analysis['elements']:
        print(f"Found {element['type']}: {element['text']}")
        print(f"Purpose: {element['purpose']}")
        print(f"Location: {element['location']}")
```

### 2. Multi-Modal Element Detection

The agent combines multiple computer vision techniques:

```python
# Traditional CV + Claude AI
cv_analysis = agent.vision_analyzer.analyze_image(screenshot)
claude_analysis = agent.claude_client.analyze_screenshot(screenshot_bytes)

# Combined insights
buttons_cv = cv_analysis.get('buttons', [])
elements_claude = claude_analysis.get('elements', [])

# Cross-reference for better accuracy
for claude_elem in elements_claude:
    if claude_elem['type'] == 'button':
        # Find matching CV detection
        for cv_button in buttons_cv:
            # Spatial matching logic
            pass
```

### 3. Advanced OCR and Text Analysis

```python
# Extract text with position information
text_elements = agent.vision_analyzer.extract_text_with_positions(screenshot)

for text_elem in text_elements:
    print(f"Text: '{text_elem['text']}'")
    print(f"Confidence: {text_elem['confidence']}%")
    print(f"Position: {text_elem['center']}")

# Find specific text on screen
position = agent.vision_analyzer.find_text_on_screen("Submit", screenshot)
if position:
    agent.click_at(position[0], position[1])
```

## Intelligent Task Planning

### Natural Language Task Execution

```python
# Complex task with natural language
task = """
Search for 'machine learning courses' on Google,
click on the first educational website result,
find the enrollment button, and take a screenshot
of the course catalog page
"""

result = agent.execute_task(task)

if result['status'] == 'completed':
    print("Task completed successfully!")
    for step in result['steps']:
        print(f"Step {step['step_number']}: {step['status']}")
```

### AI-Assisted Decision Making

```python
# Get Claude's recommendation for next action
current_state = "On Google search results page for 'AI courses'"
goal = "Find and click on a reputable online course"
available_actions = ["click_first_result", "scroll_down", "refine_search"]

decision = agent.claude_client.decide_next_action(
    current_state, goal, available_actions
)

print(f"Recommended: {decision['recommended_action']}")
print(f"Reasoning: {decision['reasoning']}")
print(f"Confidence: {decision['confidence']}")
```

## Advanced Use Cases

### 1. Intelligent Form Filling

```python
# Claude analyzes form structure and fills appropriately
def smart_form_filling(agent, form_data):
    # Analyze the form first
    screenshot = agent.capture_screen()
    analysis = agent.claude_client.analyze_screenshot(
        screenshot, "Identify all form fields and their purposes"
    )
    
    # Map data to fields intelligently
    for element in analysis.get('elements', []):
        if element['type'] == 'input':
            purpose = element['purpose'].lower()
            
            if 'email' in purpose:
                agent.web_automator.type_in_element(
                    element['selector'], form_data['email']
                )
            elif 'name' in purpose:
                agent.web_automator.type_in_element(
                    element['selector'], form_data['name']
                )
```

### 2. Adaptive Web Scraping

```python
def intelligent_scraping(agent, target_info):
    # Navigate to website
    agent.navigate_to(target_info['url'])
    
    # Let Claude analyze the page structure
    screenshot = agent.capture_screen()
    analysis = agent.claude_client.analyze_screenshot(
        screenshot, f"Find elements containing {target_info['data_type']}"
    )
    
    # Extract data based on Claude's analysis
    extracted_data = []
    for element in analysis.get('elements', []):
        if target_info['data_type'].lower() in element['purpose'].lower():
            # Extract data from this element
            data = agent.web_automator.get_element_text(element['selector'])
            extracted_data.append(data)
    
    return extracted_data
```

### 3. Multi-Application Workflow

```python
def cross_app_workflow(agent):
    plan = agent.claude_client.plan_task("""
    1. Take a screenshot of the current application
    2. Open a web browser
    3. Search for information related to what was on screen
    4. Copy relevant information back to the original application
    """)
    
    # Execute with error handling and adaptation
    for step in plan['steps']:
        success = agent.task_executor._execute_single_step(step)
        if not success:
            # Ask Claude for alternative approach
            alt_plan = agent.claude_client.decide_next_action(
                f"Step failed: {step['description']}",
                "Complete the workflow successfully",
                ["retry", "skip", "alternative_approach"]
            )
            # Handle based on Claude's recommendation
```

## Performance Optimization

### 1. Efficient Screenshot Analysis

```python
# Cache analysis results
class CachedAnalysis:
    def __init__(self, agent):
        self.agent = agent
        self.cache = {}
    
    def analyze_with_cache(self, screenshot):
        # Use image hash for caching
        import hashlib
        img_hash = hashlib.md5(screenshot.tobytes()).hexdigest()
        
        if img_hash not in self.cache:
            self.cache[img_hash] = self.agent.analyze_screen()
        
        return self.cache[img_hash]
```

### 2. Selective Claude Usage

```python
# Use Claude only for complex decisions
def smart_element_interaction(agent, element_description):
    # Try traditional CV first
    cv_result = agent.vision_analyzer.detect_buttons(screenshot)
    
    if len(cv_result) == 1:
        # Clear result, no need for Claude
        return cv_result[0]
    elif len(cv_result) > 1:
        # Ambiguous, ask Claude to choose
        claude_decision = agent.claude_client.interpret_ui_element(
            element_description, 
            f"Multiple candidates found: {cv_result}"
        )
        return claude_decision
    else:
        # No results, let Claude analyze the whole screen
        return agent.claude_client.analyze_screenshot(screenshot, element_description)
```

## Error Handling and Recovery

### Intelligent Error Recovery

```python
def robust_task_execution(agent, task_description):
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
            result = agent.execute_task(task_description)
            
            if result['status'] == 'completed':
                return result
            elif result['status'] == 'failed':
                # Ask Claude for recovery strategy
                recovery_plan = agent.claude_client.plan_task(
                    f"Recover from failed task: {result['error']}\n"
                    f"Original task: {task_description}"
                )
                
                # Execute recovery plan
                agent.execute_task(recovery_plan['description'])
                
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            
            # Wait and retry with Claude's guidance
            time.sleep(2 ** attempt)  # Exponential backoff
```

## Best Practices

### 1. Task Design
- **Be specific** in task descriptions for Claude
- **Break complex tasks** into smaller, manageable steps
- **Provide context** about the current application or website

### 2. Performance
- **Cache results** when possible to reduce API calls
- **Use traditional CV** for simple, deterministic tasks
- **Reserve Claude** for complex reasoning and ambiguous situations

### 3. Error Handling
- **Always include timeouts** for operations
- **Implement retry logic** with exponential backoff
- **Log all interactions** for debugging and analysis

### 4. Security
- **Validate all inputs** before execution
- **Limit automation scope** to authorized applications
- **Monitor for unexpected behavior** and implement kill switches

## Troubleshooting

### Common Issues

1. **Claude API Rate Limits**
   - Implement request queuing and rate limiting
   - Cache responses when possible
   - Use batch processing for multiple similar requests

2. **Screen Analysis Accuracy**
   - Ensure good screenshot quality (high resolution)
   - Provide clear context in prompts to Claude
   - Combine multiple detection methods for verification

3. **Element Detection Failures**
   - Verify element visibility and accessibility
   - Use multiple selectors (CSS, XPath, text-based)
   - Implement fallback detection methods

4. **Task Planning Issues**
   - Break down complex tasks into simpler components
   - Provide more specific context and constraints
   - Validate each step before execution

## Integration Examples

See the `examples/` directory for complete working examples:
- `basic_interaction.py` - Simple screen interaction
- `web_automation.py` - Web browsing and form filling
- `vision_analysis.py` - Computer vision demonstrations
- `advanced_agent_demo.py` - Full featured agent showcase

## API Reference

For detailed API documentation, see the docstrings in each module:
- `ComputerAgent` - Main agent interface
- `ClaudeClient` - Claude API integration
- `VisionAnalyzer` - Computer vision capabilities
- `WebAutomator` - Web automation features
- `TaskExecutor` - Task planning and execution