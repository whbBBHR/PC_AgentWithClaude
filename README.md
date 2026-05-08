# PC Agent with Claude

A powerful computer-using agent that can interact with computer interfaces, perform web searches, navigate pages, execute complex tasks, and process documents using AI decision-making powered by Claude Sonnet 4.5 API.

## Features

- 🖥️ **Screen Interaction**: Capture screenshots, detect UI elements, click, scroll, and type
- 🌐 **Web Automation**: Browse websites, navigate pages, fill forms, and interact with web elements
- 🦆 **DuckDuckGo Search**: Privacy-focused search automation demo
- 📄 **Document Processing**: AI-powered document summarization, rewriting, and analysis with interactive file browser
- 🔍 **Computer Vision**: Analyze screen content and identify interactive elements
- 🤖 **AI-Powered**: Uses Claude Sonnet 4.5 API for intelligent decision making and task planning
- 📋 **Task Execution**: Plan and execute complex multi-step computer tasks with extended action support (`capture`, `generate_report`, `output`, `scroll`, `key`, and more)
- 🎯 **Element Detection**: Smart UI element recognition and interaction
- 📁 **File Browser**: Interactive document selection with directory navigation

## Installation

```bash
# Clone or navigate to the project
cd PC_AgentWithClaude

# Create and activate virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp config.example.json config.json
```

## Configuration

### API Key (recommended)

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
```

The agent automatically loads this file regardless of the working directory. No changes to `config.json` are required.

### config.json (optional override)

If you prefer to set the key in `config.json`:

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

> ⚠️ `config.json` and `config.json.backup` are listed in `.gitignore` to prevent accidental API key exposure.

## Quick Start

### Run the advanced demo
```bash
python advanced_automation_demo.py
```
The demo detects your API key automatically and shows setup instructions only if it is missing.

### Basic screen interaction
```bash
python examples/basic_interaction.py
```

### DuckDuckGo search demo
```bash
python duckduckgo_demo.py
```

### Document processing
```bash
# Interactive document processor
python document_processor.py

# Run comprehensive demo
python demo_document_processing.py
```

## Usage Examples

### Computer Automation
```python
from src.pc_agent import ComputerAgent

agent = ComputerAgent()

# Natural language task
agent.execute_task("Search for 'Python programming' on Google and click the first result")

# Direct control
agent.web_search("AI computer vision libraries")
agent.click_element("first search result")
agent.scroll_page("down", 3)
```

### Document Processing
```python
from document_processor import DocumentProcessor, SummaryStyle, RewriteStyle

processor = DocumentProcessor()

document = processor.load_document('path/to/document.txt')

# Summarize
summary = processor.summarize_document(document, SummaryStyle.EXECUTIVE)

# Rewrite
rewrite = processor.rewrite_document(document, RewriteStyle.PROFESSIONAL)

# Multi-document analysis
analysis = processor.analyze_multiple_documents([doc1, doc2], 'comparison')
```

### Basic Screen Interaction
```python
screenshot = agent.capture_screen()
agent.click_at(100, 200)
agent.type_text("Hello, World!")
agent.scroll("down", 5)
```

### Web Navigation
```python
agent.navigate_to("https://example.com")
agent.click_element_by_text("Sign In")
agent.fill_form({"username": "user@example.com", "password": "••••••••"})
agent.submit_form()
```

### Advanced Task Execution
```python
task = """
1. Open a web browser
2. Navigate to GitHub
3. Search for 'computer vision'
4. Click on the first repository
5. Take a screenshot of the README
"""

result = agent.execute_complex_task(task)
```

## Supported Task Actions

The task executor handles the following action types from Claude's plan:

| Action | Aliases | Description |
|---|---|---|
| `click` | — | Click a UI element |
| `type` | — | Type text |
| `navigate` | — | Open a URL |
| `wait` | — | Pause execution |
| `analyze` | — | Analyze screen content |
| `scroll` | — | Scroll the page |
| `key` | — | Press a keyboard key |
| `capture` | `screenshot`, `capture_screen` | Take and optionally save a screenshot |
| `generate_report` | `report`, `summarize`, `summary` | Generate an AI report from context |
| `output` | `display`, `print`, `save` | Display or save output to file |

## API Reference

### ComputerAgent

- `capture_screen()` — Take a screenshot
- `click_at(x, y)` — Click at coordinates
- `click_element(selector)` — Click a UI element
- `type_text(text)` — Type text
- `scroll_page(direction, amount)` — Scroll the page
- `navigate_to(url)` — Open a URL
- `web_search(query)` — Perform a web search
- `execute_task(description)` — Execute a natural language task
- `analyze_screen()` — Analyze current screen content
- `plan_task(objective)` — Create a task execution plan

### DocumentProcessor

- `browse_and_select_document()` — Interactive file browser
- `load_document(file_path)` — Load a document
- `summarize_document(document, style, length)` — AI summarization
- `rewrite_document(document, style, instructions)` — Document rewriting
- `analyze_multiple_documents(documents, analysis_type)` — Multi-document analysis
- `save_result(result, filename)` — Save results as JSON/Markdown

**Summary styles**: brief, executive, bullet, detailed, academic, narrative  
**Rewrite styles**: professional, academic, casual, technical, creative  
**File formats**: `.txt`, `.md`, `.pdf`, `.docx`, `.doc`

## Examples

See the `examples/` directory:

- `basic_interaction.py` — Basic screen and keyboard interaction
- `web_automation.py` — Web browsing and form filling
- `advanced_agent_demo.py` — Multi-step task execution with navigation recovery
- `vision_analysis.py` — Computer vision and screen analysis

Top-level demos:

- `advanced_automation_demo.py` — Full system demo with API key detection
- `duckduckgo_demo.py` — Privacy-focused search automation
- `document_processor.py` — Interactive document processing
- `demo_document_processing.py` — Comprehensive document processing demo

## Requirements

- Python 3.8+
- numpy >= 2.0 (required by opencv-python 4.12+)
- OpenCV for computer vision
- Selenium/Playwright for web automation
- Anthropic API access for Claude Sonnet 4.5
- Document processing libraries (PyPDF2, python-docx, openpyxl)
- Rich console library for enhanced UI
- Platform-specific dependencies (see `requirements.txt`)

> **Note for conda users**: If using the `ClaudePytorch` conda environment, upgrade numpy to 2.x before running (`pip install "numpy>=2.0"`), as opencv-python 4.12+ requires it.

## License

MIT License — see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

- Create an issue in the repository
- Check the documentation in `docs/`
- Review example code in `examples/`
