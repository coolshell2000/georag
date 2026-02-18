"""Test map search functionality."""
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    print("1. Loading GeoRAG...")
    page.goto("http://127.0.0.1:5000")
    page.wait_for_load_state("networkidle")
    
    # 2. Switch to Map View
    print("2. Switching to Map View...")
    page.click("button:has-text('Map View')")
    time.sleep(1) # Wait for map filter/render
    
    # Check map container visibility
    map_container = page.query_selector("#map-container")
    assert map_container.is_visible(), "Map container not visible"
    print("   ✅ Map container visible")
    
    # Check for markers (leaflet-marker-icon class)
    # Wait a bit for markers to be added
    time.sleep(2)
    markers = page.query_selector_all(".leaflet-marker-icon")
    print(f"   ✅ Found {len(markers)} markers on the map")
    assert len(markers) >= 5, f"Expected at least 5 markers, found {len(markers)}"
    
    # 3. Click a marker
    print("3. Clicking a marker...")
    markers[0].click()
    time.sleep(1)
    
    # Check popup content
    popup = page.query_selector(".leaflet-popup-content")
    assert popup is not None, "Popup not found"
    text = popup.inner_text()
    print(f"   ✅ Popup content: {text}")
    assert "Download" in text, "Download link not found in popup"
    
    # Screenshot
    page.screenshot(path="/tmp/georag_map_view.png", full_page=True)
    print("   ✅ Screenshot saved: /tmp/georag_map_view.png")
    
    print("\n🎉 Map tests passed!")
    browser.close()
