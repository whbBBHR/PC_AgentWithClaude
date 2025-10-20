# PC Agent with Claude

A powerful computer-using agent that can interact with computer interfaces, perform web searches, navigate pages, execute complex tasks, and process documents using AI decision-making powered by Claude Sonnet 4.5 API.

## Features

- 🖥️ **Screen Interaction**: Capture screenshots, detect UI elements, click, scroll, and type
- 🌐 **Web Automation**: Browse websites, navigate pages, fill forms, and interact with web elements
- 📄 **Document Processing**: AI-powered document summarization, rewriting, and analysis with interactive file browser
- 🔍 **Computer Vision**: Analyze screen content and identify interactive elements
- 🤖 **AI-Powered**: Uses Claude Sonnet 4.5 API for intelligent decision making and task planning
- 📋 **Task Execution**: Plan and execute complex multi-step computer tasks
- 🎯 **Element Detection**: Smart UI element recognition and interaction
- 📁 **File Browser**: Interactive document selection with directory navigation

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

### Document Processing
```bash
# Interactive document processor
python document_processor.py

# Run comprehensive demo
python demo_document_processing.py
```

### Computer Automation
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

### Document Processing API
```python
from document_processor import DocumentProcessor, SummaryStyle

# Initialize processor
processor = DocumentProcessor()

# Load and summarize a document
document = processor.load_document('path/to/document.txt')
result = processor.summarize_document(document, SummaryStyle.EXECUTIVE)

# Rewrite document in different style
rewrite_result = processor.rewrite_document(document, RewriteStyle.PROFESSIONAL)

# Analyze multiple documents
analysis = processor.analyze_multiple_documents([doc1, doc2], 'comparison')
```

## Usage Examples

### Document Processing
```python
# Interactive file browser and document processing
from document_processor import DocumentProcessor

processor = DocumentProcessor()

# Browse and select documents interactively
selected_file = processor.browse_and_select_document()
document = processor.load_document(selected_file)

# Summarize with different styles
executive_summary = processor.summarize_document(document, SummaryStyle.EXECUTIVE)
bullet_summary = processor.summarize_document(document, SummaryStyle.BULLET)

# Rewrite documents
professional_version = processor.rewrite_document(document, RewriteStyle.PROFESSIONAL)
academic_version = processor.rewrite_document(document, RewriteStyle.ACADEMIC)

# Multi-document analysis
comparison = processor.analyze_multiple_documents([doc1, doc2], 'comparison')
```

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

### DocumentProcessor Class

#### Document Loading and Processing
- `browse_and_select_document()` - Interactive file browser
- `load_document(file_path)` - Load document from file
- `summarize_document(document, style, length)` - AI-powered summarization
- `rewrite_document(document, style, instructions)` - Document rewriting
- `analyze_multiple_documents(documents, analysis_type)` - Multi-document analysis
- `save_result(result, filename)` - Save results in JSON/Markdown

#### Supported Styles
- **Summary Styles**: brief, executive, bullet, detailed, academic, narrative
- **Rewrite Styles**: professional, academic, casual, technical, creative
- **Analysis Types**: comparison, synthesis, themes, summary

#### Supported File Formats
- Text files (.txt)
- Markdown files (.md)
- PDF documents (.pdf)
- Word documents (.docx, .doc)

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
- `demo_document_processing.py` - Comprehensive document processing demo

### Document Processing Examples

#### Interactive Mode
```bash
# Launch interactive document processor
python document_processor.py
```

#### Programmatic Usage
```python
# Batch document processing
from document_processor import DocumentProcessor, SummaryStyle, RewriteStyle

processor = DocumentProcessor()

# Process multiple documents
documents = ['doc1.txt', 'doc2.pdf', 'doc3.docx']
for doc_path in documents:
    doc = processor.load_document(doc_path)
    summary = processor.summarize_document(doc, SummaryStyle.EXECUTIVE)
    processor.save_result(summary, f"summary_{doc['file_name']}")
```

## Requirements

- Python 3.8+
- OpenCV for computer vision
- Selenium/Playwright for web automation
- Anthropic API access for Claude Sonnet 4.5 integration
- Document processing libraries (PyPDF2, python-docx, openpyxl)
- Rich console library for enhanced UI
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
