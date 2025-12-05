#!/usr/bin/env python3
"""
Test script to check Claude API connectivity
"""
import json
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from pc_agent import ClaudeClient

# Load environment variables from .env file
load_dotenv()

console = Console()

def test_api_key_from_config():
    """Test API key from config.json"""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        api_key = config.get('anthropic_api_key', '')
        
        if api_key == 'your-claude-api-key-here' or not api_key:
            console.print("❌ No valid API key found in config.json", style="red")
            return None
        
        console.print(f"✅ Found API key in config.json (starts with: {api_key[:15]}...)", style="green")
        return api_key
        
    except Exception as e:
        console.print(f"❌ Error reading config.json: {e}", style="red")
        return None

def test_api_key_from_env():
    """Test API key from environment variable"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if api_key:
        console.print(f"✅ Found API key in environment (starts with: {api_key[:15]}...)", style="green")
        return api_key
    else:
        console.print("❌ No API key found in ANTHROPIC_API_KEY environment variable", style="red")
        return None

def test_claude_connection(api_key):
    """Test actual Claude API connection"""
    try:
        console.print("🔄 Testing Claude API connection...", style="yellow")
        
        # Create Claude client with the API key
        claude = ClaudeClient(api_key=api_key)
        
        # Use the test_connection method
        result = claude.test_connection()
        
        if result.get("status") == "success":
            console.print("✅ Claude API connection successful!", style="green")
            console.print(f"Model: {result.get('model', 'Unknown')}", style="blue")
            console.print(f"Message: {result.get('message', '')}", style="blue")
            return True
        else:
            console.print(f"❌ Connection test failed: {result.get('message', 'Unknown error')}", style="red")
            return False
        
    except Exception as e:
        console.print(f"❌ Claude API connection failed: {e}", style="red")
        console.print(f"Error type: {type(e).__name__}", style="yellow")
        return False

def main():
    console.print(Panel.fit("🤖 Claude API Connection Test", style="bold blue"))
    
    # Test 1: Check config.json
    console.print("\n📋 Checking config.json for API key...")
    api_key = test_api_key_from_config()
    
    # Test 2: Check environment variable
    if not api_key:
        console.print("\n🌍 Checking environment variables...")
        api_key = test_api_key_from_env()
    
    # Test 3: Test actual API connection
    if api_key:
        console.print("\n🚀 Testing Claude API connection...")
        success = test_claude_connection(api_key)
        
        if success:
            console.print(Panel.fit("✅ All tests passed! Claude API is working.", style="green"))
        else:
            console.print(Panel.fit("❌ API key found but connection failed.", style="red"))
    else:
        console.print(Panel.fit("❌ No valid API key found. Please add your Claude API key.", style="red"))
        console.print("\n💡 To fix this:")
        console.print("1. Add your API key to config.json, or")
        console.print("2. Set environment variable: export ANTHROPIC_API_KEY='your-key-here'")

if __name__ == "__main__":
    main()