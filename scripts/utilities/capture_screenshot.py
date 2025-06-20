#!/usr/bin/env python3
"""Take screenshot using playwright"""

import asyncio
from playwright.async_api import async_playwright

async def take_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set viewport
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Navigate to the report
        print("Navigating to http://localhost:8888/llm-call-verification-improved.html")
        await page.goto("http://localhost:8888/llm-call-verification-improved.html")
        
        # Wait for content
        await page.wait_for_selector("h1", timeout=5000)
        
        # Take screenshot
        screenshot_path = "verification-report-screenshot.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot saved to {screenshot_path}")
        
        # Get page title and basic info
        title = await page.title()
        h1 = await page.text_content("h1")
        
        print(f"\nPage Info:")
        print(f"Title: {title}")
        print(f"H1: {h1}")
        
        # Count elements
        tables = await page.locator("table").count()
        cards = await page.locator(".card-hover").count()
        code_blocks = await page.locator("pre").count()
        
        print(f"\nPage Analysis:")
        print(f"Tables: {tables}")
        print(f"Cards: {cards}")
        print(f"Code blocks: {code_blocks}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(take_screenshot())