#!/usr/bin/env python3
"""
DuckDuckGo Search Demo
Demonstrates using DuckDuckGo as the search engine
"""

import sys
sys.path.insert(0, '.')

from src.pc_agent.web_automator import WebAutomator
import json
import time
import subprocess

def main():
    print('🦆 DuckDuckGo Search Automation Demo\n')
    print('=' * 60)
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    print('\n1️⃣ Initializing Web Automator...')
    automator = WebAutomator(config)
    
    try:
        print('\n2️⃣ Opening DuckDuckGo homepage...')
        if automator.navigate_to('https://duckduckgo.com'):
            # Bring browser to foreground
            browser_name = config.get('browser', 'Safari').capitalize()
            subprocess.run(['osascript', '-e', f'tell application "{browser_name}" to activate'], 
                         check=False, capture_output=True)
            
            print(f'\n✅ {browser_name} opened showing DuckDuckGo!')
            print(f'   URL: {automator.driver.current_url}')
            print(f'   Title: {automator.driver.title}')
            
            print('\n⏳ Pausing for 5 seconds...')
            time.sleep(5)
            
            # Test 1: Python automation
            print('\n3️⃣ Searching DuckDuckGo for "Python automation"...')
            if automator.search('Python automation', engine='duckduckgo'):
                print('✅ Search completed!')
                print(f'   Results page: {automator.driver.title}')
                
                print('\n⏳ Pausing for 8 seconds to view results...')
                time.sleep(8)
            
            # Test 2: Claude AI
            print('\n4️⃣ Searching DuckDuckGo for "Claude AI assistant"...')
            if automator.search('Claude AI assistant', engine='duckduckgo'):
                print('✅ Search completed!')
                print(f'   Results page: {automator.driver.title}')
                
                print('\n⏳ Pausing for 8 seconds to view results...')
                time.sleep(8)
            
            # Test 3: Web automation
            print('\n5️⃣ Searching DuckDuckGo for "Selenium web automation"...')
            if automator.search('Selenium web automation', engine='duckduckgo'):
                print('✅ Search completed!')
                print(f'   Results page: {automator.driver.title}')
                
                print('\n⏳ Pausing for 8 seconds to view results...')
                time.sleep(8)
            
            print('\n6️⃣ Closing browser in 3 seconds...')
            time.sleep(3)
            automator.driver.quit()
            
            print('\n' + '=' * 60)
            print('✅ DuckDuckGo Demo Complete!')
            print('=' * 60)
            print('\n📊 Search engines available:')
            print('   • google')
            print('   • bing')
            print('   • duckduckgo')
            print('\nUsage: automator.search("query", engine="duckduckgo")')
            
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
