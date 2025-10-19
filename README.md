# PC Agent with Claude

A powerful computer-using agent that can interact with computer interfaces, perform web searches, navigate pages, and execute complex tasks using AI decision-making powered by Claude API.

## Features

- 🖥️ **Screen Interaction**: Capture screenshots, detect UI elements, click, scroll, and type
- 🌐 **Web Automation**: Browse websites, navigate pages, fill forms, and interact with web elements
- 🔍 **Computer Vision**: Analyze screen content and identify interactive elements
- 🤖 **AI-Powered**: Uses Claude API for intelligent decision making and task planning
- 📋 **Task Execution**: Plan and execute complex multi-step computer tasks
- 🎯 **Element Detection**: Smart UI element recognition and interaction

## Installation

```bash
# Clone or navigate to the project
cd PC_AgentWithClaude

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp config.example.json config.json
# Edit config.json with your API keys and settings
```

## Quick Start

```python
from src.pc_agent import ComputerAgent

# Initialize the agent
agent = ComputerAgent()

# Perform a simple task
agent.execute_task("Search for 'Python programming' on Google and click the first result")

# Use with specific instructions
agent.web_search("AI computer vision libraries")
agent.click_element("first search result")
agent.scroll_page("down", 3)
```

## Usage Examples

### Basic Screen Interaction
```python
# Take a screenshot
screenshot = agent.capture_screen()

# Click at coordinates
agent.click_at(100, 200)

# Type text
agent.type_text("Hello, World!")

# Scroll
agent.scroll("down", 5)
```

### Web Navigation
```python
# Open a website
agent.navigate_to("https://example.com")

# Find and click an element
agent.click_element_by_text("Sign In")

# Fill a form
agent.fill_form({
    "username": "user@example.com",
    "password": "password123"
})

# Submit form
agent.submit_form()
```

### Advanced Task Execution
```python
# Complex multi-step task
task = """
1. Open a web browser
2. Navigate to GitHub
3. Search for 'computer vision'
4. Click on the first repository
5. Take a screenshot of the README
"""

result = agent.execute_complex_task(task)
```

## Configuration

Create a `config.json` file with your settings:

```json
{
    "anthropic_api_key": "your-claude-api-key",
    "screenshot_path": "./screenshots",
    "browser": "chrome",
    "headless": false,
    "wait_timeout": 10,
    "debug_mode": true
}
```

## API Reference

### ComputerAgent Class

#### Screen Interaction Methods
- `capture_screen()` - Take a screenshot
- `click_at(x, y)` - Click at specific coordinates
- `click_element(selector)` - Click on UI element
- `type_text(text)` - Type text
- `scroll_page(direction, amount)` - Scroll the page

#### Web Automation Methods
- `navigate_to(url)` - Open a URL
- `web_search(query)` - Perform web search
- `find_elements(selector)` - Find page elements
- `fill_form(data)` - Fill web forms

#### AI-Powered Methods
- `execute_task(description)` - Execute natural language tasks
- `analyze_screen()` - Analyze current screen content
- `plan_task(objective)` - Create task execution plan

## Examples

See the `examples/` directory for complete usage examples:

- `basic_interaction.py` - Basic screen and keyboard interaction
- `web_automation.py` - Web browsing and form filling
- `complex_tasks.py` - Multi-step task execution
- `vision_analysis.py` - Computer vision and screen analysis

## Requirements

- Python 3.8+
- OpenCV for computer vision
- Selenium/Playwright for web automation
- Anthropic API access for Claude integration
- Platform-specific dependencies (see requirements.txt)

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions:
- Create an issue in the repository
- Check the documentation in `docs/`
- Review example code in `examples/`
