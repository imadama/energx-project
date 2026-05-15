#!/usr/bin/env python3
"""Test the thuisbatterij wizard step-by-step and capture screenshots at each action."""

from playwright.sync_api import sync_playwright

URL = "http://localhost:5173/energx-thuisbatterij.html"
OUT = "/Users/emi/Documents/GitHub/energx-project/screenshots"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(1500)

        # ---- 1. Scroll to wizard section and screenshot ----
        page.evaluate("""
            const el = document.querySelector('#wizard-sectie');
            if (el) el.scrollIntoView({behavior: 'instant', block: 'start'});
        """)
        page.wait_for_timeout(800)
        page.screenshot(path=f"{OUT}/tb_01_wizard_initial.png", full_page=False)
        print("Saved tb_01_wizard_initial.png — wizard section before any interaction")

        # Debug: what cards exist in the zonnepanelen group?
        cards_info = page.evaluate("""
            () => {
                const cards = document.querySelectorAll('#qZonnepanelen .choice-card');
                return Array.from(cards).map(c => ({
                    dataValue: c.getAttribute('data-value'),
                    text: c.innerText.trim().replace(/\\n/g,' ').substring(0, 80),
                    visible: c.offsetParent !== null
                }));
            }
        """)
        print("\nZonnepanelen cards:", cards_info)

        # ---- 2. Click first choice-card in #qZonnepanelen (Ja, ik heb zonnepanelen) ----
        first_zonnepanelen = page.locator('#qZonnepanelen .choice-card').first
        first_zonnepanelen.scroll_into_view_if_needed()
        first_zonnepanelen.click()
        page.wait_for_timeout(600)
        page.screenshot(path=f"{OUT}/tb_02_after_zonnepanelen.png", full_page=False)
        print("Saved tb_02_after_zonnepanelen.png — after clicking first zonnepanelen option")

        # ---- 3. Click first goal card in #qDoel ----
        doel_cards = page.evaluate("""
            () => {
                const cards = document.querySelectorAll('#qDoel .choice-card');
                return Array.from(cards).map(c => ({
                    dataValue: c.getAttribute('data-value'),
                    text: c.innerText.trim().replace(/\\n/g,' ').substring(0, 60)
                }));
            }
        """)
        print("\nDoel cards:", doel_cards)

        first_doel = page.locator('#qDoel .choice-card').first
        first_doel.scroll_into_view_if_needed()
        first_doel.click()
        page.wait_for_timeout(600)
        page.screenshot(path=f"{OUT}/tb_03_after_doel.png", full_page=False)
        print("Saved tb_03_after_doel.png — after clicking first goal card")

        # ---- 4. Click first verbruik option in #qVerbruik ----
        verbruik_cards = page.evaluate("""
            () => {
                const cards = document.querySelectorAll('#qVerbruik .choice-card');
                return Array.from(cards).map(c => ({
                    dataValue: c.getAttribute('data-value'),
                    text: c.innerText.trim().replace(/\\n/g,' ').substring(0, 60)
                }));
            }
        """)
        print("\nVerbruik cards:", verbruik_cards)

        first_verbruik = page.locator('#qVerbruik .choice-card').first
        first_verbruik.scroll_into_view_if_needed()
        first_verbruik.click()
        page.wait_for_timeout(600)
        page.screenshot(path=f"{OUT}/tb_04_after_verbruik.png", full_page=False)
        print("Saved tb_04_after_verbruik.png — after clicking first verbruik option")

        # ---- 5. Click first cap-card in #qCapaciteit ----
        cap_cards = page.evaluate("""
            () => {
                const cards = document.querySelectorAll('#qCapaciteit .cap-card');
                return Array.from(cards).map(c => ({
                    dataValue: c.getAttribute('data-value'),
                    text: c.innerText.trim().replace(/\\n/g,' ').substring(0, 80)
                }));
            }
        """)
        print("\nCapaciteit cards:", cap_cards)

        first_cap = page.locator('#qCapaciteit .cap-card').first
        first_cap.scroll_into_view_if_needed()
        first_cap.click()
        page.wait_for_timeout(600)
        page.screenshot(path=f"{OUT}/tb_05_after_capaciteit.png", full_page=False)
        print("Saved tb_05_after_capaciteit.png — after clicking first capaciteit card")

        # ---- 6. Click "Bekijk jouw advies →" button ----
        bekijk_btn = page.locator('button.btn-wiz-next', has_text='Bekijk jouw advies')
        btn_visible = bekijk_btn.is_visible()
        print(f"\n'Bekijk jouw advies' button visible: {btn_visible}")

        # Scroll it into view and click
        bekijk_btn.scroll_into_view_if_needed()
        page.wait_for_timeout(400)

        # Capture state just before clicking
        page.screenshot(path=f"{OUT}/tb_06_before_bekijk_click.png", full_page=False)
        print("Saved tb_06_before_bekijk_click.png — just before clicking Bekijk jouw advies")

        bekijk_btn.click()
        page.wait_for_timeout(800)  # wait for slide animation (0.42s transition)

        # ---- 7. Screenshot AFTER clicking to see where wizard is ----
        # First scroll back to wizard-sectie top so we see the full wizard
        page.evaluate("""
            const el = document.querySelector('#wizard-sectie');
            if (el) el.scrollIntoView({behavior: 'instant', block: 'start'});
        """)
        page.wait_for_timeout(400)
        page.screenshot(path=f"{OUT}/tb_07_after_bekijk_click.png", full_page=False)
        print("Saved tb_07_after_bekijk_click.png — AFTER clicking Bekijk jouw advies")

        # ---- Inspect the slide state ----
        slide_state = page.evaluate("""
            () => {
                const track = document.getElementById('wizardSlides');
                const inner = track ? track.parentElement : null;
                return {
                    trackTransform: track ? window.getComputedStyle(track).transform : 'N/A',
                    trackInlineTransform: track ? track.style.transform : 'N/A',
                    innerHeight: inner ? inner.style.height : 'N/A',
                    innerComputedHeight: inner ? window.getComputedStyle(inner).height : 'N/A',
                };
            }
        """)
        print("\nSlide state after click:", slide_state)

        # Check visibility of each wizard block
        block_visibility = page.evaluate("""
            () => {
                const blocks = ['wizardStep1', 'wizardAdvies', 'wizardStep2', 'wizardStep3', 'formSuccess'];
                return blocks.map(id => {
                    const el = document.getElementById(id);
                    if (!el) return {id, found: false};
                    const style = window.getComputedStyle(el);
                    return {
                        id,
                        found: true,
                        display: style.display,
                        visibility: style.visibility,
                        opacity: style.opacity,
                        offsetLeft: el.offsetLeft,
                        offsetTop: el.offsetTop
                    };
                });
            }
        """)
        print("\nWizard block states after click:")
        for b in block_visibility:
            print(f"  #{b.get('id')}: display={b.get('display')} visibility={b.get('visibility')} opacity={b.get('opacity')} offsetLeft={b.get('offsetLeft')}")

        # Full-page screenshot to see if advies content scrolled below
        page.screenshot(path=f"{OUT}/tb_08_after_bekijk_fullpage.png", full_page=True)
        print("Saved tb_08_after_bekijk_fullpage.png — full page after click")

        # Check if wizardAdvies block has content rendered
        advies_info = page.evaluate("""
            () => {
                const el = document.getElementById('wizardAdvies');
                if (!el) return 'NOT FOUND';
                return {
                    innerHTML_snippet: el.innerHTML.substring(0, 400).replace(/\\n/g, ' '),
                    hasVergCards: el.querySelectorAll('.verg-card').length,
                    boundingRect: JSON.stringify(el.getBoundingClientRect())
                };
            }
        """)
        print("\nwizardAdvies info:", advies_info)

        browser.close()
        print("\nDone.")

if __name__ == "__main__":
    run()
