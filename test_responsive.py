"""Test responsive layout."""
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    
    # Wait for stats to load
    with page.expect_response("**/stats") as response_info:
        page.goto("http://127.0.0.1:5000")
    print(f"   ✅ Stats loaded: {response_info.value.json()}")
    
    # Check container width
    container = page.query_selector(".container")
    box = container.bounding_box()
    print(f"   ✅ Container width: {box['width']}px")
    
    # Expected width: 1920 * 0.95 = 1824px
    expected = 1920 * 0.95
    assert abs(box['width'] - expected) < 50, f"Expected width ~{expected}, got {box['width']}"
    print(f"   ✅ Width matches 95% of viewport")
    
    # Switch to Map View to screenshot wide map
    page.click("button:has-text('Map View')")
    time.sleep(1)
    
    page.screenshot(path="/tmp/georag_wide_map.png", full_page=True)
    print("   ✅ Screenshot saved: /tmp/georag_wide_map.png")
    
    browser.close()
