#!/usr/bin/env python3
"""Slow-motion web automation demo"""

import sys
sys.path.insert(0, '.')

from src.pc_agent.web_automator import WebAutomator
import json
import time
import subprocess

print('🌐 SLOW-MOTION Web Automation Demo\n')
print('⏱️  Each step will pause for 8 seconds so you can watch!\n')

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

automator = WebAutomator(config)

print('=' * 60)
print('STEP 1: Opening Safari and loading Google.com...')
print('=' * 60)
if automator.navigate_to('https://www.google.com'):
    # Bring Safari to foreground
    subprocess.run(['osascript', '-e', 'tell application "Safari" to activate'], check=False)
    
    print('✅ Safari is now open - LOOK AT YOUR SCREEN!')
    print(f'   Page: {automator.driver.title}')
    print('\n⏳ Waiting 8 seconds - watch the Google homepage...\n')
    time.sleep(8)
    
    print('=' * 60)
    print('STEP 2: Searching for "Python automation"...')
    print('=' * 60)
    if automator.search('Python automation'):
        print('✅ Search submitted!')
        print('\n⏳ Waiting 8 seconds - watch the search results appear...\n')
        time.sleep(8)
        
        print('=' * 60)
        print('STEP 3: Going to Wikipedia.org...')
        print('=' * 60)
        automator.navigate_to('https://www.wikipedia.org')
        print('✅ Now on Wikipedia!')
        print('\n⏳ Waiting 8 seconds - see the Wikipedia homepage...\n')
        time.sleep(8)
        
        print('=' * 60)
        print('STEP 4: Going to Python.org...')
        print('=' * 60)
        automator.navigate_to('https://www.python.org')
        print('✅ Now on Python.org!')
        print('\n⏳ Waiting 8 seconds - see the Python homepage...\n')
        time.sleep(8)
        
        print('=' * 60)
        print('STEP 5: Going to GitHub.com...')
        print('=' * 60)
        automator.navigate_to('https://www.github.com')
        print('✅ Now on GitHub!')
        print('\n⏳ Waiting 10 seconds - see the GitHub homepage...\n')
        time.sleep(10)
        
    print('=' * 60)
    print('CLOSING: Browser will close in 5... 4... 3... 2... 1...')
    print('=' * 60)
    time.sleep(5)
    automator.driver.quit()
    print('\n✅ Demo complete!')
else:
    print('❌ Failed to start')
    if automator.driver:
        automator.driver.quit()
