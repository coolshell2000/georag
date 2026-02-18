"""Test download heat visualization."""
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Capture console logs
    page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
    
    print("1. Loading GeoRAG...")
    # Wait for stats to load
    with page.expect_response("**/stats") as response_info:
        page.goto("http://127.0.0.1:5000")
    print(f"   ✅ Stats loaded: {response_info.value.json()}")
    
    # Search for the hot file
    print("2. Searching for 'north_sea_reflection_profile.sgy'...")
    page.fill("#searchInput", "north_sea_reflection_profile.sgy")
    time.sleep(1.5)
    page.wait_for_load_state("networkidle")
    
    # Check for hot styling
    btns = page.query_selector_all(".download-btn")
    assert len(btns) > 0, "No download buttons found"
    
    btn = btns[0]
    style = btn.get_attribute("style")
    print(f"   ✅ Button style: {style}")
    
    # Check for fire icon in count
    count_el = page.query_selector(".download-count")
    text = count_el.inner_text()
    print(f"   ✅ Count text: {text}")
    
    # Verify color is red-ish (rgb(255, 64, 0)) or icon is present
    if "🔥" in text or "rgb(255, 64, 0)" in style:
        print("   ✅ Verified HOT status (Red/Fire)")
    else:
        print("   ❌ Failed to verify HOT status")
        browser.close()
        exit(1)
        
    page.screenshot(path="/tmp/georag_hot_download.png", full_page=True)
    print("   ✅ Screenshot saved: /tmp/georag_hot_download.png")
    
    print("\n🎉 Heat visualization tests passed!")
    browser.close()
