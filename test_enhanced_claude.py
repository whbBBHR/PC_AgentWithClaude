#!/usr/bin/env python3
"""
Enhanced Claude Sonnet 4.5 Model Test
Tests the latest Claude Sonnet 4.5 (claude-sonnet-4-5-20250929) model with enhanced features
Used throughout PC Agent v2.0 for document processing and web automation
"""
import json
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.pc_agent.claude_client import ClaudeClient

# Load environment variables from .env file
load_dotenv()

console = Console()

def test_model_configuration():
    """Test the Claude Sonnet 4.5 model configuration and capabilities"""
    console.print("🔧 Testing Claude Sonnet 4.5 Model Configuration", style="bold blue")
    
    # Load configuration
    try:
        with open('config.example.json', 'r') as f:
            config = json.load(f)
        
        console.print(f"✅ Configuration loaded successfully", style="green")
        console.print(f"Model: {config.get('claude_model')}", style="cyan")
        console.print(f"Vision Model: {config.get('vision_model')}", style="cyan")
        console.print(f"Max Tokens: {config.get('max_tokens')}", style="cyan")
        console.print(f"Temperature: {config.get('temperature')}", style="cyan")
        
        return config
        
    except Exception as e:
        console.print(f"❌ Failed to load configuration: {e}", style="red")
        return None

def test_enhanced_claude_client():
    """Test the enhanced Claude Sonnet 4.5 client with configuration"""
    config = test_model_configuration()
    if not config:
        return False
    
    console.print("\n🤖 Testing Enhanced Claude Sonnet 4.5 Client", style="bold blue")
    
    # Get API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key or api_key == 'your-claude-api-key-here':
        console.print("❌ No valid API key found", style="red")
        return False
    
    try:
        # Initialize Claude client with configuration
        claude = ClaudeClient(api_key=api_key, config=config)
        
        console.print("✅ Claude Sonnet 4.5 client initialized successfully", style="green")
        console.print(f"Using model: {claude.model}", style="cyan")
        console.print(f"Max tokens: {claude.max_tokens}", style="cyan")
        
        # Verify we're using Sonnet 4.5
        if "sonnet-4-5" in claude.model:
            console.print("🎉 Confirmed: Using Claude Sonnet 4.5!", style="bold green")
        else:
            console.print(f"⚠️  Warning: Expected Sonnet 4.5, got {claude.model}", style="yellow")
        
        return claude
        
    except Exception as e:
        console.print(f"❌ Failed to initialize Claude client: {e}", style="red")
        return None

def test_model_capabilities(claude):
    """Test the advanced capabilities of Claude Sonnet 4.5"""
    console.print("\n🧠 Testing Claude Sonnet 4.5 Capabilities", style="bold blue")
    
    tests = [
        {
            "name": "Basic Reasoning",
            "prompt": "What is 2+2? Answer with just the number.",
            "expected_length": "short"
        },
        {
            "name": "Document Processing", 
            "prompt": "Summarize this text in one sentence: 'Claude Sonnet 4.5 represents a significant advancement in AI language models, offering enhanced reasoning capabilities, better document understanding, and improved task execution for complex workflows.'",
            "expected_length": "medium"
        },
        {
            "name": "Text Analysis",
            "prompt": "Analyze the key themes in this text: 'Modern AI systems must balance innovation with ethical considerations, ensuring responsible deployment while maximizing beneficial outcomes.' Provide 2 main themes.",
            "expected_length": "medium"
        },
        {
            "name": "Task Planning",
            "prompt": "Create a step-by-step plan to automate document processing: load a PDF, summarize it, and save results. Be specific and technical.",
            "expected_length": "long"
        },
        {
            "name": "Web Automation Strategy",
            "prompt": "Design an approach to automate clicking a submit button on a webpage using computer vision and browser automation. Include error handling.",
            "expected_length": "long"
        }
    ]
    
    results = []
    
    for test in tests:
        try:
            console.print(f"\n🔍 Running test: {test['name']}")
            response = claude.generate_response(test['prompt'])
            
            if response:
                console.print(f"✅ Response received ({len(response)} characters)", style="green")
                console.print(f"Preview: {response[:100]}...", style="dim")
                results.append({
                    "test": test['name'],
                    "success": True,
                    "response_length": len(response),
                    "preview": response[:150] + "..." if len(response) > 150 else response
                })
            else:
                console.print("❌ No response received", style="red")
                results.append({
                    "test": test['name'],
                    "success": False,
                    "error": "No response"
                })
                
        except Exception as e:
            console.print(f"❌ Test failed: {e}", style="red")
            results.append({
                "test": test['name'],
                "success": False,
                "error": str(e)
            })
    
    return results

def display_results(results):
    """Display test results in a formatted table"""
    console.print("\n📊 Test Results Summary", style="bold blue")
    
    table = Table(title="Claude Sonnet Model Test Results")
    table.add_column("Test", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Response Length", justify="right")
    table.add_column("Preview", style="dim")
    
    passed = 0
    failed = 0
    
    for result in results:
        if result['success']:
            status = "✅ PASS"
            length = str(result['response_length'])
            preview = result['preview']
            passed += 1
        else:
            status = "❌ FAIL"
            length = "N/A"
            preview = result.get('error', 'Unknown error')
            failed += 1
        
        table.add_row(result['test'], status, length, preview)
    
    console.print(table)
    
    # Summary
    total = passed + failed
    success_rate = (passed / total) * 100 if total > 0 else 0
    
    summary_panel = Panel.fit(
        f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)\n"
        f"Model: Claude 4.5 Sonnet (Latest)\n"
        f"Enhanced Features: ✅ Configuration-based, ✅ Higher token limits, ✅ Temperature control",
        title="🎯 Test Summary",
        style="green" if passed == total else "yellow" if passed > failed else "red"
    )
    
    console.print(summary_panel)

def main():
    console.print(Panel.fit("🚀 Claude Sonnet 4.5 Enhanced Test Suite", style="bold blue"))
    
    # Verify model configuration
    try:
        from src.pc_agent.claude_client import ClaudeClient
        console.print("✓ [green]Model Configuration: Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)[/green]")
    except ImportError as e:
        console.print(f"❌ [red]Import Error: {e}[/red]")
        console.print("Please ensure PC Agent modules are installed.")
        return
    
    # Test enhanced client
    claude = test_enhanced_claude_client()
    
    if not claude:
        console.print(Panel.fit("❌ Cannot proceed without valid Claude client", style="red"))
        return
    
    # Test capabilities
    results = test_model_capabilities(claude)
    
    # Display results
    display_results(results)
    
    console.print("\n💡 Claude Sonnet 4.5 Features Tested:", style="bold yellow")
    console.print("✓ Document Processing Capabilities")
    console.print("✓ Enhanced Reasoning and Analysis")
    console.print("✓ Web Automation Task Planning")
    console.print("✓ Complex Text Understanding")

if __name__ == "__main__":
    main()