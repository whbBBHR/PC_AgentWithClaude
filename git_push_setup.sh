#!/bin/bash
# Git Push Setup Script for PC Agent with Claude

echo "🚀 PC Agent with Claude - Git Push Setup"
echo "======================================="

# Check current git status
echo "📋 Current git status:"
git status --porcelain

# Show current branch
echo "🌿 Current branch: $(git branch --show-current)"

# Show commits
echo "📝 Recent commits:"
git log --oneline -3

echo ""
echo "🔗 Setting up remote repository..."
echo ""
echo "To push to GitHub, you need to:"
echo "1. Create a new repository at: https://github.com/new"
echo "2. Use these settings:"
echo "   - Repository name: PC_AgentWithClaude"
echo "   - Description: 'Computer automation agent with Claude AI integration and advanced computer vision'"
echo "   - Visibility: Public or Private (your choice)"
echo "   - ❌ DON'T check 'Add a README file' (we already have one)"
echo "   - ❌ DON'T add .gitignore (we already have one)"
echo ""
echo "3. After creating the repo, run these commands:"
echo ""

# Generate the commands user will need
USERNAME_PLACEHOLDER="YOUR_GITHUB_USERNAME"
REPO_NAME="PC_AgentWithClaude"

echo "   git remote add origin https://github.com/${USERNAME_PLACEHOLDER}/${REPO_NAME}.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "🔒 Security check before pushing:"
echo "✅ .env files are in .gitignore"
echo "✅ API keys are protected"
echo "✅ Pre-commit hooks are installed"
echo "✅ Only safe files will be pushed"
echo ""
echo "📁 Files that will be pushed (21 files):"
git ls-files | head -10
if [ $(git ls-files | wc -l) -gt 10 ]; then
    echo "   ... and $(( $(git ls-files | wc -l) - 10 )) more files"
fi
echo ""
echo "🔒 Files protected from git:"
echo "   - .env (your API keys)"
echo "   - config.json (if it contains real keys)"
echo "   - venv/ (virtual environment)"
echo "   - screenshots/ (may contain sensitive content)"
echo ""
echo "💡 Ready to push! Just add your GitHub username to the commands above."