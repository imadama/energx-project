#!/usr/bin/env python3
"""Test wizard form on energx-laadpaal.html and capture screenshots."""

from playwright.sync_api import sync_playwright

URL = "http://localhost:5173/energx-laadpaal.html"
OUT_DIR = "/Users/emi/Documents/GitHub/energx-project/screenshots"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(1500)

        # ---- Screenshot 1: Full page before interaction ----
        page.screenshot(path=f"{OUT_DIR}/01_full_page.png", full_page=True)
        print("Saved 01_full_page.png")

        # ---- Scroll to wizard section ----
        page.evaluate("""
            const el = document.querySelector('#wizard-sectie');
            if (el) el.scrollIntoView({behavior: 'instant', block: 'start'});
        """)
        page.wait_for_timeout(800)
        page.screenshot(path=f"{OUT_DIR}/02_wizard_section.png", full_page=False)
        print("Saved 02_wizard_section.png")

        # ---- Q1: "Ja, interessant" — first choice-card in #q1 ----
        q1_ja = page.locator("#q1 .choice-card[data-value='ja']")
        q1_ja.click()
        page.wait_for_timeout(500)
        page.screenshot(path=f"{OUT_DIR}/03_after_q1.png", full_page=False)
        print("Saved 03_after_q1.png — clicked Q1 'Ja, interessant'")

        # ---- Q2: "Ja, ik heb zonnepanelen" ----
        q2_ja = page.locator("#q2 .choice-card[data-value='ja']")
        q2_ja.click()
        page.wait_for_timeout(500)
        page.screenshot(path=f"{OUT_DIR}/04_after_q2.png", full_page=False)
        print("Saved 04_after_q2.png — clicked Q2 'Ja, ik heb zonnepanelen'")

        # ---- Q3: "Niet nodig" ----
        q3_nee = page.locator("#q3 .choice-card[data-value='nee']")
        q3_nee.click()
        page.wait_for_timeout(500)
        page.screenshot(path=f"{OUT_DIR}/05_after_q3.png", full_page=False)
        print("Saved 05_after_q3.png — clicked Q3 'Niet nodig'")

        # ---- Q4: "Niet nodig" ----
        q4_nee = page.locator("#q4 .choice-card[data-value='nee']")
        q4_nee.click()
        page.wait_for_timeout(1000)
        page.screenshot(path=f"{OUT_DIR}/06_after_q4.png", full_page=False)
        print("Saved 06_after_q4.png — clicked Q4 'Niet nodig'")

        # ---- Check what's visible now ----
        # Scroll a bit to see what appeared below the questions
        page.evaluate("window.scrollBy(0, 300)")
        page.wait_for_timeout(600)
        page.screenshot(path=f"{OUT_DIR}/07_scroll_down.png", full_page=False)
        print("Saved 07_scroll_down.png")

        # Full page from wizard top to see comparison section
        page.evaluate("""
            const el = document.querySelector('#wizard-sectie');
            if (el) el.scrollIntoView({behavior: 'instant', block: 'start'});
        """)
        page.wait_for_timeout(400)
        page.screenshot(path=f"{OUT_DIR}/08_wizard_after_fullpage.png", full_page=True)
        print("Saved 08_wizard_after_fullpage.png")

        # ---- Debug: Check for comparison/product cards ----
        cards_info = page.evaluate("""
            () => {
                // Look for visible comparison blocks
                const allCards = document.querySelectorAll('.verg-card, .product-card, [class*="verg"], [class*="card"]');
                return Array.from(allCards).map(c => {
                    const img = c.querySelector('img');
                    const style = window.getComputedStyle(c);
                    return {
                        tagName: c.tagName,
                        className: c.className,
                        visible: c.offsetParent !== null && style.display !== 'none' && style.visibility !== 'hidden',
                        display: style.display,
                        hasImage: !!img,
                        imgSrc: img ? img.src : null,
                        imgAlt: img ? img.alt : null,
                        text: c.innerText.substring(0, 150).replace(/\\n/g, ' | ')
                    };
                });
            }
        """)
        print("\n--- CARD / COMPARISON ELEMENTS ---")
        for c in cards_info:
            print(f"  {c['tagName']}.{c['className'][:50]}  visible={c['visible']}  display={c['display']}  hasImg={c['hasImage']}  imgSrc={c['imgSrc']}")
            if c['text']:
                print(f"     text: {c['text'][:120]}")

        # Check progress / which block is visible
        visible_blocks = page.evaluate("""
            () => {
                const blocks = document.querySelectorAll('[class*="wizard-block"], [id*="Step"], [id*="step"]');
                return Array.from(blocks).map(b => ({
                    id: b.id,
                    className: b.className,
                    display: window.getComputedStyle(b).display,
                    visible: b.offsetParent !== null
                }));
            }
        """)
        print("\n--- WIZARD BLOCK VISIBILITY ---")
        for b in visible_blocks:
            print(f"  #{b['id']} .{b['className'][:50]}  display={b['display']}  visible={b['visible']}")

        # Check if there's a comparison/recommendation section
        comparison_html = page.evaluate("""
            () => {
                const el = document.querySelector('#vergelijking') || document.querySelector('[id*="verg"]') || document.querySelector('[class*="aanbeveling"]');
                return el ? {id: el.id, class: el.className, html: el.outerHTML.substring(0, 3000)} : 'NOT FOUND';
            }
        """)
        print("\n--- COMPARISON SECTION ---")
        if isinstance(comparison_html, dict):
            print(f"id={comparison_html['id']}  class={comparison_html['class']}")
            print(comparison_html['html'][:2000])
        else:
            print(comparison_html)

        browser.close()
        print("\nDone.")

if __name__ == "__main__":
    run()
