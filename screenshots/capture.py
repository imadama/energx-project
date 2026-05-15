from playwright.sync_api import sync_playwright

def capture(url, output_path, viewport_width=1280, viewport_height=900):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': viewport_width, 'height': viewport_height})
        page.goto(url, wait_until='networkidle')
        page.screenshot(path=output_path, full_page=True)
        browser.close()

capture('http://localhost:5173/', '/Users/emi/Documents/GitHub/energx-project/screenshots/desktop_1280x900.png', 1280, 900)
print("Screenshot saved.")
