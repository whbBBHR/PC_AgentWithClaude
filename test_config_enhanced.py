#!/usr/bin/env python3
"""
Enhanced Configuration Test for PC_AgentWithClaude
Tests the new configuration-driven approach without requiring API keys
"""

import json
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import our enhanced modules
from src.pc_agent.claude_client import ClaudeClient

console = Console()

def test_enhanced_configuration():
    """Test the enhanced configuration system"""
    console.print(Panel.fit("🔧 Testing Enhanced Configuration System", style="bold blue"))
    
    # Load configuration
    config_path = "config.json" if os.path.exists("config.json") else "config.example.json"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    console.print(f"✅ Configuration loaded from: {config_path}")
    
    # Test configuration parsing
    table = Table(title="Enhanced Configuration Settings")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green") 
    table.add_column("Type", style="yellow")
    
    # Enhanced Claude settings
    claude_model = config.get('claude_model', 'claude-3-5-sonnet-20241022')
    vision_model = config.get('vision_model', 'claude-3-5-sonnet-20241022')
    max_tokens = config.get('max_tokens', 4000)
    temperature = config.get('temperature', 0.1)
    step_delay = config.get('step_delay', 0.5)
    
    table.add_row("Claude Model", claude_model, "Model Selection")
    table.add_row("Vision Model", vision_model, "Vision Model") 
    table.add_row("Max Tokens", str(max_tokens), "Token Limit")
    table.add_row("Temperature", str(temperature), "Response Control")
    table.add_row("Step Delay", f"{step_delay}s", "Timing Control")
    
    console.print(table)
    
    return config

def test_claude_client_enhancement():
    """Test the enhanced Claude client initialization"""
    console.print(Panel.fit("🤖 Testing Enhanced Claude Client", style="bold green"))
    
    config_path = "config.json" if os.path.exists("config.json") else "config.example.json"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Test Claude client initialization with config
    try:
        # Use a dummy API key for testing initialization
        client = ClaudeClient("dummy_key_for_testing", config)
        
        console.print("✅ ClaudeClient initialized with enhanced configuration")
        console.print(f"   Model: {client.model}")
        console.print(f"   Vision Model: {client.vision_model}")
        console.print(f"   Max Tokens: {client.max_tokens}")
        console.print(f"   Temperature: {client.temperature}")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Error initializing ClaudeClient: {str(e)}")
        return False

def test_anthropic_library_version():
    """Test the anthropic library version"""
    console.print(Panel.fit("📚 Testing Anthropic Library", style="bold magenta"))
    
    try:
        import anthropic
        version = anthropic.__version__
        console.print(f"✅ Anthropic library version: {version}")
        
        # Check if it's the latest version
        if version >= "0.71.0":
            console.print(f"✅ Latest anthropic library installed (>= 0.71.0)")
        else:
            console.print(f"⚠️  Consider upgrading anthropic library (current: {version})")
            
        return True
        
    except ImportError as e:
        console.print(f"❌ Error importing anthropic: {str(e)}")
        return False

def main():
    """Run all enhanced configuration tests"""
    console.print(Panel.fit("🚀 PC_AgentWithClaude Enhanced Configuration Test", style="bold white"))
    
    results = {}
    
    # Test enhanced configuration
    try:
        config = test_enhanced_configuration()
        results['config'] = True
    except Exception as e:
        console.print(f"❌ Configuration test failed: {str(e)}")
        results['config'] = False
    
    console.print()
    
    # Test anthropic library
    results['anthropic'] = test_anthropic_library_version()
    console.print()
    
    # Test Claude client enhancement
    results['claude_client'] = test_claude_client_enhancement()
    console.print()
    
    # Summary
    console.print(Panel.fit("📊 Test Results Summary", style="bold cyan"))
    
    summary_table = Table()
    summary_table.add_column("Test", style="cyan")
    summary_table.add_column("Result", style="bold")
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        summary_table.add_row(test_name.replace('_', ' ').title(), status)
    
    console.print(summary_table)
    
    all_passed = all(results.values())
    if all_passed:
        console.print(Panel.fit("🎉 All Enhancement Tests Passed!", style="bold green"))
        console.print("Your PC_AgentWithClaude is ready with Claude 3.5 Sonnet enhanced capabilities!")
    else:
        console.print(Panel.fit("⚠️  Some Tests Failed", style="bold yellow"))

if __name__ == "__main__":
    main()