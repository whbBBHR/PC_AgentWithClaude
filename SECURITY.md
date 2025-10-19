# Security Guidelines for PC Agent with Claude

## 🔒 API Key Security

### Environment Variables Setup
1. **Never commit API keys to git!**
2. Use `.env` file for local development
3. Use environment variables for production

### Setup Instructions

#### Step 1: Create `.env` file
```bash
cp .env.example .env
```

#### Step 2: Add your API key to `.env`
```bash
# Edit .env file and replace placeholder with your actual key
ANTHROPIC_API_KEY="your-production-key-here"
```

#### Step 3: Verify `.gitignore` protection
The `.gitignore` file already protects:
- `.env` files
- `config.json` (contains API key)
- `secrets/` directory
- All key files (`*.key`, `*.pem`)

## 🛡️ Git Security Checklist

### Before First Commit
- [ ] Verify `.env` is in `.gitignore`
- [ ] Check no API keys are in tracked files
- [ ] Use `.env.example` as template (safe to commit)

### Before Each Push
```bash
# Check for accidentally staged secrets
git status
git diff --cached

# Scan for potential API keys
grep -r "api-key-pattern" . --exclude-dir=.git --exclude-dir=venv
```

### Emergency: If API Key Was Committed
1. **Immediately revoke the API key** at https://console.anthropic.com/
2. Generate a new API key
3. Remove from git history:
   ```bash
   git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch path/to/file' --prune-empty --tag-name-filter cat -- --all
   ```

## 🔐 Production Deployment

### Environment Variables
```bash
# Set in production environment
export ANTHROPIC_API_KEY="your-production-key"
export DEBUG=false
export LOG_LEVEL=WARNING
```

### Docker Security
```dockerfile
# Use secrets management
RUN --mount=type=secret,id=anthropic_key \
    ANTHROPIC_API_KEY="$(cat /run/secrets/anthropic_key)"
```

### CI/CD Security
- Use encrypted environment variables
- Never echo API keys in logs
- Use secret management services

## 📋 Security Best Practices

1. **Rotate API keys regularly**
2. **Use separate keys for dev/staging/prod**
3. **Monitor API usage** for unusual activity
4. **Set up rate limits** and billing alerts
5. **Review access logs** periodically

## 🚨 Emergency Contacts

- Anthropic Security: security@anthropic.com
- API Key Issues: support@anthropic.com