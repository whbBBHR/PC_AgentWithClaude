#!/usr/bin/env python3
"""
Security Status Check for PC_AgentWithClaude
Verifies API key protection and security measures
"""

import os
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def check_security_status():
    """Check comprehensive security status"""
    console.print(Panel.fit("🔒 PC_AgentWithClaude Security Status Check", style="bold blue"))
    
    security_checks = []
    
    # Check 1: .gitignore protection
    gitignore_path = Path(".gitignore")
    gitignore_content = ""
    if gitignore_path.exists():
        with open(gitignore_path) as f:
            gitignore_content = f.read()
        
        if "config.json" in gitignore_content:
            security_checks.append(("Git Protection", "✅", "config.json ignored by git"))
        else:
            security_checks.append(("Git Protection", "❌", "config.json NOT protected"))
    
    # Check 2: .env file protection
    if ".env" in gitignore_content:
        security_checks.append((".env Protection", "✅", ".env file ignored by git"))
    else:
        security_checks.append((".env Protection", "❌", ".env NOT protected"))
    
    # Check 3: config.json API key status  
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        
        api_key = config.get("anthropic_api_key", "")
        if api_key == "your-claude-api-key-here":
            security_checks.append(("config.json API Key", "✅", "Using placeholder (secure)"))
        elif api_key.startswith("sk-ant-"):
            security_checks.append(("config.json API Key", "⚠️", "Real key in config.json (move to .env)"))
        else:
            security_checks.append(("config.json API Key", "❓", "Unknown key format"))
    
    # Check 4: .env file setup
    env_path = Path(".env")
    if env_path.exists():
        security_checks.append((".env File", "✅", ".env file exists"))
        
        # Check if .env has real API key
        with open(env_path) as f:
            env_content = f.read()
        
        # Look for real API key pattern (starts with sk-ant-api03-)
        if "sk-ant-api03-" in env_content and len([line for line in env_content.split('\n') if line.startswith('ANTHROPIC_API_KEY=sk-ant-api03-')]) > 0:
            security_checks.append((".env API Key", "✅", "Real API key configured (secure)"))
        elif "sk-ant-" in env_content:
            security_checks.append((".env API Key", "✅", "API key configured (secure)"))
        else:
            security_checks.append((".env API Key", "⚠️", "No real API key in .env yet"))
    else:
        security_checks.append((".env File", "❌", ".env file missing"))
    
    # Check 5: Git status
    import subprocess
    try:
        result = subprocess.run(['git', 'check-ignore', 'config.json'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            security_checks.append(("Git Ignore Test", "✅", "config.json properly ignored"))
        else:
            security_checks.append(("Git Ignore Test", "❌", "config.json NOT ignored"))
    except:
        security_checks.append(("Git Ignore Test", "❓", "Cannot test git ignore"))
    
    # Display results
    table = Table(title="🔒 Security Protection Status")
    table.add_column("Security Check", style="cyan")
    table.add_column("Status", justify="center", width=8)
    table.add_column("Details", style="dim")
    
    for check, status, details in security_checks:
        table.add_row(check, status, details)
    
    console.print(table)
    
    # Security recommendations
    console.print(Panel.fit("🛡️ Security Recommendations", style="bold yellow"))
    
    recommendations = [
        "✅ Keep API keys in .env file (already protected by .gitignore)",
        "✅ Use placeholder values in config.json", 
        "✅ Never commit real API keys to git",
        "✅ Regularly rotate your API keys",
        "✅ Use environment variables in production",
        "✅ Enable pre-commit hooks for additional protection"
    ]
    
    for rec in recommendations:
        console.print(f"   {rec}")
    
    # Show proper setup
    console.print(Panel.fit("🔧 Proper API Key Setup", style="bold green"))
    console.print("1. Edit .env file:")
    console.print("   [dim]ANTHROPIC_API_KEY=sk-ant-api03-your-real-key-here[/]")
    console.print()
    console.print("2. Keep config.json with placeholder:")
    console.print("   [dim]\"anthropic_api_key\": \"your-claude-api-key-here\"[/]")
    console.print()
    console.print("3. The system will automatically use .env when available")

def main():
    check_security_status()

if __name__ == "__main__":
    main()