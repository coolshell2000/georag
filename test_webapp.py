"""End-to-end test for GeoRAG web application."""
from playwright.sync_api import sync_playwright
import json
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # 1. Load the page
    print("1. Loading GeoRAG...")
    page.goto("http://127.0.0.1:5000")
    page.wait_for_load_state("networkidle")
    assert "GeoRAG" in page.title(), f"Unexpected title: {page.title()}"
    print("   ✅ Page loaded successfully")

    # 2. Search for earthquakes
    print("2. Searching for 'earthquake'...")
    page.fill("#searchInput", "earthquake")
    time.sleep(1)  # debounce
    page.wait_for_load_state("networkidle")
    time.sleep(1)

    results = page.query_selector_all(".result-card")
    assert len(results) > 0, "No search results found"
    print(f"   ✅ Found {len(results)} results")

    # Verify Tohoku earthquake appears
    content = page.content()
    assert "tohoku" in content.lower(), "Tohoku earthquake not in results"
    print("   ✅ Tohoku earthquake data found in results")

    # 3. Screenshot the search results
    page.screenshot(path="/tmp/georag_search_results.png", full_page=True)
    print("   ✅ Screenshot saved: /tmp/georag_search_results.png")

    # 4. Search for ocean
    print("3. Searching for 'ocean temperature'...")
    page.fill("#searchInput", "ocean temperature")
    time.sleep(1)
    page.wait_for_load_state("networkidle")
    time.sleep(1)

    content = page.content()
    assert "pacific_ocean" in content.lower(), "Pacific Ocean SST not in results"
    print("   ✅ Pacific Ocean SST dataset found in results")

    # 5. Search for gravity
    print("4. Searching for 'gravity survey'...")
    page.fill("#searchInput", "gravity survey")
    time.sleep(1)
    page.wait_for_load_state("networkidle")
    time.sleep(1)

    content = page.content()
    assert "bouguer" in content.lower(), "Bouguer gravity survey not in results"
    print("   ✅ Bouguer gravity survey found in results")

    # 6. Screenshot gravity results
    page.screenshot(path="/tmp/georag_gravity_results.png", full_page=True)
    print("   ✅ Screenshot saved: /tmp/georag_gravity_results.png")

    # 7. Search for seismic
    print("5. Searching for 'seismic reflection'...")
    page.fill("#searchInput", "seismic reflection")
    time.sleep(1)
    page.wait_for_load_state("networkidle")
    time.sleep(1)

    content = page.content()
    assert "north_sea" in content.lower(), "North Sea reflection profile not in results"
    print("   ✅ North Sea SEG-Y profile found in results")

    # Final screenshot
    page.screenshot(path="/tmp/georag_seismic_results.png", full_page=True)
    print("   ✅ Screenshot saved: /tmp/georag_seismic_results.png")

    print("\n🎉 All tests passed!")
    browser.close()
