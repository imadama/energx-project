#!/usr/bin/env python3
"""Inspect wizard DOM to find actual button texts."""

from playwright.sync_api import sync_playwright

URL = "http://localhost:5173/energx-laadpaal.html"
OUT_DIR = "/Users/emi/Documents/GitHub/energx-project/screenshots"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(1500)

        # Get all buttons on the page
        buttons = page.evaluate("""
            () => {
                const btns = document.querySelectorAll('button');
                return Array.from(btns).map(b => ({
                    text: b.innerText.trim(),
                    visible: b.offsetParent !== null,
                    classes: b.className
                }));
            }
        """)
        print("ALL BUTTONS ON PAGE:")
        for b in buttons:
            print(f"  visible={b['visible']}  text={repr(b['text'])}  class={b['classes'][:60]}")

        # Get wizard section HTML
        wizard_html = page.evaluate("""
            () => {
                const el = document.querySelector('#wizard-sectie') || document.querySelector('[id*="wizard"]') || document.querySelector('[class*="wizard"]');
                if (el) return el.outerHTML.substring(0, 5000);
                return 'WIZARD NOT FOUND - all IDs: ' + Array.from(document.querySelectorAll('[id]')).map(e=>e.id).join(', ');
            }
        """)
        print("\n--- WIZARD HTML ---")
        print(wizard_html[:3000])

        browser.close()

if __name__ == "__main__":
    run()
