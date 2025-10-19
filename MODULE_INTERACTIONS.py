"""
PC Agent with Claude - Module Interaction Diagram
================================================

                    🎯 USER INPUT
                         │
                         ▼
    ╔════════════════════════════════════════════════════════╗
    ║                  ⚡ TaskExecutor                       ║
    ║  ┌──────────────────────────────────────────────────┐  ║
    ║  │  Core Methods:                                   │  ║
    ║  │  • execute_task(description)                     │  ║
    ║  │  • plan_and_execute()                            │  ║
    ║  │  • coordinate_components()                       │  ║
    ║  │  • handle_errors()                               │  ║
    ║  │  • set_components(agent, claude, vision, web)    │  ║
    ║  └──────────────────────────────────────────────────┘  ║
    ╚════════════════════════════════════════════════════════╝
         │            │            │            │
         ▼            ▼            ▼            ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
    │   🤖    │ │   🖥️    │ │   👁️    │ │   🌐    │
    │ Claude  │ │Computer │ │ Vision  │ │   Web   │
    │ Client  │ │ Agent   │ │Analyzer │ │Automator│
    └─────────┘ └─────────┘ └─────────┘ └─────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   🤖 CLAUDE_CLIENT.PY                          │
├─────────────────────────────────────────────────────────────────┤
│  Main Functions:                                                │
│  ├── analyze_screenshot(image_data, task_description)           │
│  ├── plan_task(task_description, context)                      │
│  ├── decide_next_action(current_state, goal)                   │
│  ├── chat(message)                                             │
│  └── evaluate_result(action_result, expected_outcome)          │
│                                                                 │
│  Dependencies:                                                  │
│  ├── anthropic (Claude API)                                    │
│  ├── base64 (Image encoding)                                   │
│  └── json (Data processing)                                    │
└─────────────────────────────────────────────────────────────────┘
                         │ ▲
                    Sends│ │Returns
                   Images│ │Analysis
                         ▼ │
┌─────────────────────────────────────────────────────────────────┐
│                  🖥️ COMPUTER_AGENT.PY                         │
├─────────────────────────────────────────────────────────────────┤
│  Screen Control:                                                │
│  ├── capture_screen() → screenshot.png                         │
│  ├── click_at(x, y) → mouse click                              │
│  ├── type_text(text) → keyboard input                          │
│  ├── scroll_page(direction, amount) → scroll                   │
│  ├── drag_and_drop(start_x, start_y, end_x, end_y)            │
│  └── get_window_info() → window details                        │
│                                                                 │
│  Application Control:                                           │
│  ├── launch_application(app_name)                              │
│  ├── close_application(app_name)                               │
│  ├── switch_window(window_title)                               │
│  └── minimize_window()                                         │
│                                                                 │
│  Dependencies:                                                  │
│  ├── pyautogui (GUI automation)                                │
│  ├── pynput (Advanced input control)                           │
│  └── screeninfo (Display information)                          │
└─────────────────────────────────────────────────────────────────┘
                         │ ▲
                   Sends │ │ Returns
             Screenshots │ │ Analysis
                         ▼ │
┌─────────────────────────────────────────────────────────────────┐
│                   👁️ VISION_ANALYZER.PY                       │
├─────────────────────────────────────────────────────────────────┤
│  Image Processing:                                              │
│  ├── analyze_image(image_path) → element_list                  │
│  ├── detect_text(image) → OCR_results                          │
│  ├── find_buttons(image) → button_coordinates                  │
│  ├── identify_ui_elements(image) → UI_map                      │
│  ├── compare_images(img1, img2) → similarity_score             │
│  └── extract_colors(image) → color_palette                     │
│                                                                 │
│  Element Detection:                                             │
│  ├── locate_element_by_text(text, image)                       │
│  ├── find_clickable_areas(image)                               │
│  ├── detect_form_fields(image)                                 │
│  └── identify_navigation_elements(image)                       │
│                                                                 │
│  Dependencies:                                                  │
│  ├── opencv-python (Image processing)                          │
│  ├── pytesseract (OCR)                                         │
│  ├── PIL (Image manipulation)                                  │
│  └── numpy (Array processing)                                  │
└─────────────────────────────────────────────────────────────────┘
                         │ ▲
                   Sends │ │ Returns
              Page Data │ │ Analysis
                         ▼ │
┌─────────────────────────────────────────────────────────────────┐
│                   🌐 WEB_AUTOMATOR.PY                          │
├─────────────────────────────────────────────────────────────────┤
│  Browser Control:                                               │
│  ├── open_browser(url) → WebDriver instance                    │
│  ├── navigate_to(url) → page navigation                        │
│  ├── click_element(selector) → element interaction             │
│  ├── fill_form_field(selector, value) → form input            │
│  ├── submit_form(form_selector) → form submission              │
│  └── take_screenshot() → page screenshot                       │
│                                                                 │
│  Page Interaction:                                              │
│  ├── scroll_to_element(selector)                               │
│  ├── wait_for_element(selector, timeout)                       │
│  ├── extract_page_text() → page content                        │
│  ├── get_page_title() → document title                         │
│  ├── handle_alerts() → alert management                        │
│  └── switch_tabs() → tab navigation                            │
│                                                                 │
│  Data Extraction:                                               │
│  ├── scrape_table_data(table_selector)                         │
│  ├── extract_links() → link collection                         │
│  ├── get_form_data() → form analysis                           │
│  └── capture_network_requests()                                │
│                                                                 │
│  Dependencies:                                                  │
│  ├── selenium (Web automation)                                 │
│  ├── beautifulsoup4 (HTML parsing)                             │
│  └── requests (HTTP requests)                                  │
└─────────────────────────────────────────────────────────────────┘

🔄 INTERACTION PATTERNS:
═══════════════════════

1. SIMPLE DESKTOP TASK:
   TaskExecutor → ComputerAgent → VisionAnalyzer → TaskExecutor

2. AI-GUIDED TASK:
   TaskExecutor → ClaudeClient → ComputerAgent → VisionAnalyzer → ClaudeClient → TaskExecutor

3. WEB AUTOMATION:
   TaskExecutor → WebAutomator → VisionAnalyzer → ClaudeClient → TaskExecutor

4. COMPLEX MULTI-STEP:
   TaskExecutor → ClaudeClient (plan) → ComputerAgent (action) → VisionAnalyzer (verify) → 
   ClaudeClient (decide) → WebAutomator (web action) → VisionAnalyzer (analyze) → TaskExecutor

📊 DATA FLOW TYPES:
══════════════════

🔸 Image Data: ComputerAgent → VisionAnalyzer → ClaudeClient
🔸 Commands: TaskExecutor → ComputerAgent/WebAutomator  
🔸 Analysis: VisionAnalyzer → ClaudeClient → TaskExecutor
🔸 Decisions: ClaudeClient → TaskExecutor → Action Modules
🔸 Feedback: Action Results → VisionAnalyzer → ClaudeClient

🎛️ CONFIGURATION FLOW:
═════════════════════

Config Files → TaskExecutor.setup() → Component Initialization → Ready State
"""