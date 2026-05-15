from playwright.sync_api import sync_playwright
import time

URL = "http://localhost:5173/energx-thuisbatterij.html"
SCREENSHOTS_DIR = "/Users/emi/Documents/GitHub/energx-project/screenshots/"

def capture(page, name):
    path = SCREENSHOTS_DIR + name
    page.screenshot(path=path, full_page=False)
    print(f"Saved: {path}")
    return path

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})

        print("=== Navigating to page ===")
        page.goto(URL, wait_until="networkidle")
        time.sleep(1)

        print("=== Scrolling to #wizard-sectie ===")
        page.evaluate("document.querySelector('#wizard-sectie')?.scrollIntoView({behavior:'instant'})")
        time.sleep(0.5)

        # Capture slide 1 initial state
        print("=== Screenshot 1: Slide 1 — 'Heb je zonnepanelen?' ===")
        capture(page, "new_wizard_01_slide1_initial.png")

        # Check what is visible on slide 1
        slide1_text = page.inner_text("#wizard-sectie") if page.query_selector("#wizard-sectie") else "NOT FOUND"
        print(f"Wizard section visible text snippet: {slide1_text[:400]}")

        # Check all wizard slides
        slides = page.query_selector_all(".wizard-slide, .step, [data-step], .slide")
        print(f"Found {len(slides)} slide/step elements")
        for i, s in enumerate(slides):
            cls = s.get_attribute("class") or ""
            visible = s.is_visible()
            text_snippet = s.inner_text()[:80].replace("\n", " ")
            print(f"  Slide {i}: class='{cls}' visible={visible} text='{text_snippet}'")

        # ---- STEP 1: Click "Ja, ik heb zonnepanelen" ----
        print("\n=== Clicking 'Ja, ik heb zonnepanelen' ===")
        ja_option = page.query_selector("text=Ja, ik heb zonnepanelen")
        if not ja_option:
            # Try broader search
            ja_option = page.query_selector("[data-value='ja'], .option:has-text('Ja'), button:has-text('Ja')")
        if not ja_option:
            # List all clickable options
            all_options = page.query_selector_all(".wizard-option, .choice, .option-card, label")
            print(f"  Could not find 'Ja, ik heb zonnepanelen' — found {len(all_options)} generic option elements:")
            for o in all_options[:10]:
                print(f"    '{o.inner_text()[:60]}'")
        else:
            print(f"  Found option: '{ja_option.inner_text()[:60]}'")
            ja_option.click()
            time.sleep(0.8)  # wait for slide animation

        print("=== Screenshot 2: After clicking Ja zonnepanelen (should show slide 2) ===")
        capture(page, "new_wizard_02_after_zonnepanelen.png")

        # Re-check visible slides
        slides_after = page.query_selector_all(".wizard-slide, .step, [data-step], .slide")
        for i, s in enumerate(slides_after):
            visible = s.is_visible()
            if visible:
                text_snippet = s.inner_text()[:100].replace("\n", " ")
                print(f"  VISIBLE Slide {i}: '{text_snippet}'")

        # ---- STEP 2: Click a goal option ----
        print("\n=== Looking for goal options (Wat zijn je doelen?) ===")
        # Try to find goal options
        goal_option = None
        for selector in [
            "text=Zelfvoorzienend",
            "text=Besparen",
            "text=Teruglevering",
            ".wizard-option",
            ".option-card",
            ".choice",
            "label.option",
        ]:
            el = page.query_selector(selector)
            if el and el.is_visible():
                goal_option = el
                print(f"  Found goal option with selector '{selector}': '{el.inner_text()[:60]}'")
                break

        if goal_option:
            goal_option.click()
            time.sleep(0.3)
        else:
            print("  WARNING: No goal option found, trying all visible options...")
            all_visible_opts = page.query_selector_all(".wizard-option:visible, .option-card:visible")
            print(f"  Found {len(all_visible_opts)} visible options")

        # Click "Volgende →" button
        print("\n=== Clicking 'Volgende →' button ===")
        next_btn = None
        for selector in ["text=Volgende", "button:has-text('Volgende')", ".btn-next", "#next-btn", "button.next"]:
            el = page.query_selector(selector)
            if el and el.is_visible():
                next_btn = el
                print(f"  Found next button: '{el.inner_text()}'")
                break

        if next_btn:
            next_btn.click()
            time.sleep(0.8)
        else:
            print("  WARNING: No 'Volgende' button found")
            # List all visible buttons
            btns = page.query_selector_all("button")
            visible_btns = [b for b in btns if b.is_visible()]
            print(f"  Visible buttons: {[b.inner_text()[:40] for b in visible_btns]}")

        print("=== Screenshot 3: After Volgende (should show slide 3 — verbruik) ===")
        capture(page, "new_wizard_03_after_doelen.png")

        # ---- STEP 3: Click first verbruik option ----
        print("\n=== Looking for verbruik options ===")
        verbruik_option = None
        for selector in [
            "text=minder dan 2.500",
            "text=< 2.500",
            "text=2.500",
            "text=Klein",
            ".wizard-option",
            ".option-card",
        ]:
            el = page.query_selector(selector)
            if el and el.is_visible():
                verbruik_option = el
                print(f"  Found verbruik option: '{el.inner_text()[:60]}'")
                break

        if verbruik_option:
            verbruik_option.click()
            time.sleep(0.8)
        else:
            print("  WARNING: No verbruik option found")
            # Print current visible text in wizard
            wiz = page.query_selector("#wizard-sectie")
            if wiz:
                print(f"  Current wizard text: {wiz.inner_text()[:300]}")

        print("=== Screenshot 4: After verbruik click (should show slide 4 — capaciteit) ===")
        capture(page, "new_wizard_04_after_verbruik.png")

        # ---- STEP 4: Click first capaciteit option ----
        print("\n=== Looking for capaciteit options ===")
        cap_option = None
        for selector in [
            "text=5 kWh",
            "text=10 kWh",
            "text=Weet ik niet",
            "text=Klein",
            ".wizard-option",
            ".option-card",
        ]:
            el = page.query_selector(selector)
            if el and el.is_visible():
                cap_option = el
                print(f"  Found capaciteit option: '{el.inner_text()[:60]}'")
                break

        if cap_option:
            cap_option.click()
            time.sleep(0.8)
        else:
            print("  WARNING: No capaciteit option found")

        print("=== Screenshot 5: After capaciteit click (should show contact form) ===")
        capture(page, "new_wizard_05_after_capaciteit.png")

        # Check if contact form is visible
        contact_form = page.query_selector("input[name='naam'], input[name='email'], input[placeholder*='naam'], input[type='email']")
        if contact_form and contact_form.is_visible():
            print("  Contact form IS visible")
        else:
            print("  WARNING: Contact form not found or not visible")
            wiz = page.query_selector("#wizard-sectie")
            if wiz:
                print(f"  Current wizard text: {wiz.inner_text()[:300]}")

        # Check for console errors
        print("\n=== Checking for JS errors ===")
        page.on("console", lambda msg: print(f"  CONSOLE [{msg.type}]: {msg.text}") if msg.type == "error" else None)

        browser.close()
        print("\n=== Test complete ===")

if __name__ == "__main__":
    run()
