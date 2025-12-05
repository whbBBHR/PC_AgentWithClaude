# Navigation Failure Troubleshooting Guide

## ⚠️ "Navigation attempt 3 failed" Error

This warning appears when the web automation system tries to navigate to a URL but fails after 3 retry attempts.

---

## 🔍 Common Causes

### 1. **Browser Session Closed/Expired**
- **Symptom:** InvalidSessionIdException
- **Cause:** Browser window closed manually or session timed out
- **Solution:** 
  ```python
  # Re-initialize the web automator
  agent.web_automator = None
  agent.initialize_web_automator()
  ```

### 2. **WebDriver Not Initialized**
- **Symptom:** "Automator not initialized" error
- **Cause:** Web automator initialization failed
- **Solution:**
  ```bash
  # Check browser driver is available
  safaridriver --enable  # For Safari
  # or ensure ChromeDriver is installed
  ```

### 3. **Network/Firewall Issues**
- **Symptom:** Timeouts after multiple attempts
- **Cause:** URL blocked, slow network, or firewall
- **Solution:**
  - Check internet connection
  - Try a different URL (e.g., http://example.com)
  - Check firewall/VPN settings

### 4. **Safari Automation Settings**
- **Symptom:** Safari won't respond to automation commands
- **Cause:** Remote Automation not enabled
- **Solution:**
  ```bash
  # Enable Safari automation
  safaridriver --enable
  
  # Or manually: Safari > Develop > Allow Remote Automation
  ```

### 5. **Configuration Issues**
- **Symptom:** Wrong browser or missing settings
- **Cause:** config.json misconfigured
- **Solution:**
  ```json
  {
    "browser": "safari",  // or "chrome"
    "headless": false,
    "max_retries": 3,
    "wait_timeout": 10
  }
  ```

---

## 🔧 Quick Fixes

### Fix 1: Reset Browser Session
```python
# In your code:
if not agent.navigate_to(url):
    print("Navigation failed, reinitializing...")
    agent.web_automator.cleanup()
    agent.initialize_web_automator()
    agent.navigate_to(url)  # Try again
```

### Fix 2: Increase Retry Count
```python
# Navigate with more retries
success = agent.web_automator.navigate_to(url, max_retries=5)
```

### Fix 3: Add Wait Time
```python
import time

# Give browser more time to initialize
time.sleep(2)
agent.navigate_to(url)
```

### Fix 4: Check Browser Availability
```python
# Before navigation, verify browser is running
if hasattr(agent.web_automator, 'automator'):
    if agent.web_automator.automator and agent.web_automator.automator.driver:
        print("✅ Browser session active")
    else:
        print("❌ Browser session inactive, reinitializing...")
        agent.initialize_web_automator()
```

---

## 🛠️ Debugging Steps

### Step 1: Check Logs
```bash
# View recent errors
tail -50 agent.log | grep -i "navigation\|error"
```

### Step 2: Test Browser Manually
```bash
# Test Safari automation
safaridriver --enable
open -a Safari

# Test Chrome automation
chromedriver --version
```

### Step 3: Verify Configuration
```python
import json

with open('config.json') as f:
    config = json.load(f)
    print(f"Browser: {config.get('browser')}")
    print(f"Max retries: {config.get('max_retries')}")
    print(f"Timeout: {config.get('wait_timeout')}")
```

### Step 4: Test Simple Navigation
```python
# Test with a simple, reliable URL
agent.navigate_to("http://example.com")  # Should always work
```

---

## 💡 Best Practices

1. **Always check initialization:**
   ```python
   if agent.web_automator is None:
       agent.initialize_web_automator()
   ```

2. **Handle failures gracefully:**
   ```python
   for attempt in range(3):
       if agent.navigate_to(url):
           break
       print(f"Retry {attempt + 1}/3...")
       time.sleep(2)
   ```

3. **Use try-except blocks:**
   ```python
   try:
       agent.navigate_to(url)
   except Exception as e:
       print(f"Navigation error: {e}")
       agent.initialize_web_automator()  # Recover
   ```

4. **Clean up properly:**
   ```python
   try:
       # Your automation code
       pass
   finally:
       agent.cleanup()  # Always cleanup
   ```

---

## 🚨 Error Messages Reference

| Error Message | Meaning | Solution |
|--------------|---------|----------|
| "Automator not initialized" | Web automator never started | Call `initialize_web_automator()` |
| "InvalidSessionIdException" | Browser closed/crashed | Restart browser session |
| "Navigation timeout" | Page took too long to load | Increase `wait_timeout` in config |
| "Invalid URL" | Malformed URL | Check URL format (include http://) |
| "Navigation attempt X failed" | Generic failure after retries | Check logs for specific error |

---

## 📞 Still Having Issues?

1. Check Safari settings: Safari > Develop > Allow Remote Automation
2. Restart Safari/Chrome completely
3. Check for system updates
4. Verify internet connection
5. Try with a simple URL first (http://example.com)
6. Review full error logs in `agent.log`

---

## 🔄 Recovery Script

Use this script to recover from navigation failures:

```python
def recover_navigation(agent, url, max_attempts=3):
    """Attempt navigation with automatic recovery"""
    for attempt in range(max_attempts):
        try:
            # Ensure web automator exists
            if not hasattr(agent, 'web_automator') or agent.web_automator is None:
                print(f"🔄 Initializing web automator (attempt {attempt + 1})...")
                agent.initialize_web_automator()
                time.sleep(2)
            
            # Try navigation
            if agent.navigate_to(url):
                print("✅ Navigation successful!")
                return True
            
            # Failed - cleanup and retry
            print(f"⚠️  Navigation failed (attempt {attempt + 1}/{max_attempts})")
            if attempt < max_attempts - 1:
                print("🔄 Reinitializing...")
                agent.web_automator.cleanup()
                agent.web_automator = None
                time.sleep(3)
                
        except Exception as e:
            print(f"❌ Error on attempt {attempt + 1}: {e}")
            if attempt < max_attempts - 1:
                time.sleep(3)
    
    print("❌ All navigation attempts failed")
    return False

# Usage:
recover_navigation(agent, "https://www.google.com")
```
