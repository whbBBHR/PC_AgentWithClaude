#!/usr/bin/env python3
"""
Slow Browser Automation Demo - Watch Safari automate in real-time!
"""

import sys
sys.path.insert(0, '.')

from src.pc_agent.web_automator import WebAutomator
import json
import time
import subprocess

def main():
    print('🌐 SLOW Browser Automation Demo\n')
    print('=' * 60)
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    print('\n1️⃣ Initializing Web Automator...')
    automator = WebAutomator(config)
    
    try:
        print('\n2️⃣ Opening Safari and navigating to Google...')
        print('   👀 WATCH YOUR SCREEN - Safari should open now!')
        
        if automator.navigate_to('https://www.google.com'):
            # Bring Safari to foreground
            subprocess.run(['osascript', '-e', 'tell application "Safari" to activate'], 
                         check=False, capture_output=True)
            
            print('\n✅ Safari is now open showing Google!')
            print(f'   URL: {automator.driver.current_url}')
            print(f'   Title: {automator.driver.title}')
            
            print('\n⏳ Pausing for 8 seconds... (look at Safari)')
            for i in range(8, 0, -1):
                print(f'   {i}...', end=' ', flush=True)
                time.sleep(1)
            print()
            
            print('\n3️⃣ Searching for "Python automation tutorials"...')
            if automator.search('Python automation tutorials'):
                print('✅ Search query sent!')
                
                print('\n⏳ Pausing for 8 seconds... (watch search results load)')
                for i in range(8, 0, -1):
                    print(f'   {i}...', end=' ', flush=True)
                    time.sleep(1)
                print()
                
                print(f'\n📄 Current page: {automator.driver.title[:50]}')
                
                print('\n4️⃣ Navigating to Wikipedia...')
                automator.navigate_to('https://www.wikipedia.org')
                print('✅ Now on Wikipedia!')
                
                print('\n⏳ Pausing for 8 seconds... (look at Wikipedia)')
                for i in range(8, 0, -1):
                    print(f'   {i}...', end=' ', flush=True)
                    time.sleep(1)
                print()
                
                print('\n5️⃣ Going to Python.org...')
                automator.navigate_to('https://www.python.org')
                print('✅ Now on Python.org!')
                
                print('\n⏳ Pausing for 8 seconds... (look at Python.org)')
                for i in range(8, 0, -1):
                    print(f'   {i}...', end=' ', flush=True)
                    time.sleep(1)
                print()
                
                print('\n6️⃣ Final stop: GitHub...')
                automator.navigate_to('https://github.com')
                print('✅ Now on GitHub!')
                
                print('\n⏳ Pausing for 10 seconds... (look at GitHub)')
                for i in range(10, 0, -1):
                    print(f'   {i}...', end=' ', flush=True)
                    time.sleep(1)
                print()
            
            print('\n7️⃣ Closing browser in 3 seconds...')
            time.sleep(3)
            automator.driver.quit()
            
            print('\n' + '=' * 60)
            print('✅ Demo Complete!')
            print('=' * 60)
            
        else:
            print('❌ Navigation failed')
            if automator.driver:
                automator.driver.quit()
    
    except KeyboardInterrupt:
        print('\n\n⚠️ Demo interrupted by user')
        if automator.driver:
            automator.driver.quit()
    except Exception as e:
        print(f'\n❌ Error: {e}')
        if automator.driver:
            automator.driver.quit()

if __name__ == '__main__':
    main()
