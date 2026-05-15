from playwright.sync_api import sync_playwright

def capture_crop(url, output_path, viewport_width=1280, viewport_height=900, clip=None):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': viewport_width, 'height': viewport_height})
        page.goto(url, wait_until='networkidle')
        page.screenshot(path=output_path, clip=clip)
        browser.close()

# Hero section - top of page
capture_crop(
    'http://localhost:5173/',
    '/Users/emi/Documents/GitHub/energx-project/screenshots/hero_section.png',
    clip={'x': 0, 'y': 0, 'width': 1280, 'height': 600}
)

# CTA/offerte section near bottom - capture a tall region toward the end
capture_crop(
    'http://localhost:5173/',
    '/Users/emi/Documents/GitHub/energx-project/screenshots/cta_section.png',
    clip={'x': 0, 'y': 700, 'width': 1280, 'height': 400}
)

print("Crops saved.")
