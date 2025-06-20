#!/usr/bin/env python3
"""Take a screenshot of the verification dashboard using Selenium."""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def take_dashboard_screenshot():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Create driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to dashboard
        url = "http://localhost:9999/verification_dashboard_final.html"
        print(f"Opening: {url}")
        driver.get(url)
        
        # Wait for React to render
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "root")))
        time.sleep(2)  # Extra time for full render
        
        # Take screenshot
        driver.save_screenshot("verification_dashboard_screenshot.png")
        print("✅ Screenshot saved as verification_dashboard_screenshot.png")
        
        # Get page info
        title = driver.title
        body_text = driver.find_element(By.TAG_NAME, "body").text
        
        print(f"\n📊 Page Title: {title}")
        print(f"📄 Body text length: {len(body_text)} characters")
        
        if len(body_text) > 100:
            print("✅ Dashboard appears to be rendering content")
        else:
            print("❌ Dashboard may not be rendering properly")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    take_dashboard_screenshot()