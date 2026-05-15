from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1280, 'height': 900})
    page.goto('http://localhost:5173/', wait_until='networkidle')

    # Get offerte section position
    offerte_rect = page.evaluate("""() => {
        const sec = document.getElementById('offerte') || document.querySelector('section.offerte');
        if (!sec) return null;
        const r = sec.getBoundingClientRect();
        const scrollY = window.scrollY;
        return {top: r.top + scrollY, left: r.left, width: r.width, height: r.height};
    }""")
    print("Offerte rect:", offerte_rect)

    # Also get ghost button details
    ghost_details = page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('a, button')).find(el => el.textContent.trim().includes('Hoe werkt het'));
        if (!btn) return null;
        const cs = window.getComputedStyle(btn);
        return {
            backgroundColor: cs.backgroundColor,
            color: cs.color,
            border: cs.border,
            borderColor: cs.borderColor,
            text: btn.textContent.trim()
        };
    }""")
    print("Ghost button:", ghost_details)

    if offerte_rect:
        page.screenshot(
            path='/Users/emi/Documents/GitHub/energx-project/screenshots/offerte_section.png',
            full_page=True,
            clip={'x': offerte_rect['left'], 'y': offerte_rect['top'], 'width': offerte_rect['width'], 'height': min(offerte_rect['height'], 500)}
        )
        print("Offerte screenshot saved.")

    browser.close()
