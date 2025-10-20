#!/usr/bin/env python3
"""
DuckDuckGo Element Inspector
Investigate the actual HTML structure to find correct selectors
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from rich.console import Console
from rich.table import Table

console = Console()

def inspect_duckduckgo():
    """Inspect DuckDuckGo page to find actual element selectors"""
    
    console.print("🦆 Inspecting DuckDuckGo HTML Structure", style="bold cyan")
    
    try:
        # Initialize Safari WebDriver
        driver = webdriver.Safari()
        console.print("✅ Safari WebDriver initialized")
        
        # Navigate to DuckDuckGo
        driver.get("https://duckduckgo.com")
        console.print("✅ Navigated to DuckDuckGo")
        
        # Wait for page to load
        time.sleep(3)
        
        # Get page title
        console.print(f"📄 Page title: {driver.title}")
        
        # Look for all input elements
        console.print("\n🔍 Finding all input elements...")
        inputs = driver.find_elements(By.TAG_NAME, "input")
        
        if inputs:
            table = Table(title="Input Elements Found")
            table.add_column("Index", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Name", style="green")
            table.add_column("ID", style="yellow")
            table.add_column("Class", style="blue")
            table.add_column("Placeholder", style="white")
            
            for i, input_elem in enumerate(inputs):
                input_type = input_elem.get_attribute("type") or "None"
                name = input_elem.get_attribute("name") or "None"
                elem_id = input_elem.get_attribute("id") or "None"
                class_name = input_elem.get_attribute("class") or "None"
                placeholder = input_elem.get_attribute("placeholder") or "None"
                
                table.add_row(
                    str(i), input_type, name, elem_id, 
                    class_name[:30] + "..." if len(class_name) > 30 else class_name,
                    placeholder[:30] + "..." if len(placeholder) > 30 else placeholder
                )
            
            console.print(table)
        else:
            console.print("❌ No input elements found")
        
        # Look for search-related elements by various methods
        console.print("\n🎯 Trying specific search selectors...")
        
        selectors_to_test = [
            "input[name='q']",
            "input#search_form_input", 
            "input[type='text']",
            "input[type='search']",
            "[data-testid*='search']",
            "[aria-label*='search']",
            "[placeholder*='search']",
            ".search-wrap input",
            "#searchbox_input",
            "input.searchbox_input"
        ]
        
        for selector in selectors_to_test:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    console.print(f"✅ Found {len(elements)} element(s) with: {selector}")
                    for i, elem in enumerate(elements):
                        console.print(f"   Element {i}: {elem.tag_name} - visible: {elem.is_displayed()}")
                else:
                    console.print(f"❌ No elements found with: {selector}")
            except Exception as e:
                console.print(f"⚠️  Error with selector {selector}: {e}")
        
        # Get page source snippet around potential search areas
        console.print("\n📝 Page source analysis...")
        page_source = driver.page_source
        
        # Look for search-related patterns in HTML
        search_patterns = ['search', 'input', 'form', 'query']
        for pattern in search_patterns:
            if pattern in page_source.lower():
                console.print(f"✅ Found '{pattern}' in page source")
            else:
                console.print(f"❌ '{pattern}' not found in page source")
        
        # Take a screenshot for visual inspection
        driver.save_screenshot("screenshots/duckduckgo_inspection.png")
        console.print("📸 Screenshot saved: screenshots/duckduckgo_inspection.png")
        
        # Wait a bit to see the page
        console.print("\n⏸️  Keeping browser open for 10 seconds for visual inspection...")
        time.sleep(10)
        
    except Exception as e:
        console.print(f"❌ Error during inspection: {e}")
    
    finally:
        try:
            driver.quit()
            console.print("🧹 Browser closed")
        except:
            pass

if __name__ == "__main__":
    inspect_duckduckgo()