from playwright.sync_api import sync_playwright
import json

def inspect_wizard():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        page.goto('http://localhost:5173/energx-thuisbatterij.html', wait_until='networkidle')

        # 1. Computed styles for #wizardSlides
        wizard_slides = page.evaluate("""() => {
            const el = document.getElementById('wizardSlides');
            if (!el) return { error: 'Element #wizardSlides not found' };
            const cs = window.getComputedStyle(el);
            return {
                display: cs.display,
                flexDirection: cs.flexDirection,
                overflow: cs.overflow,
                width: cs.width,
                height: cs.height,
                className: el.className,
            };
        }""")

        # 2. Computed styles for .wizard-inner
        wizard_inner = page.evaluate("""() => {
            const el = document.querySelector('.wizard-inner');
            if (!el) return { error: 'Element .wizard-inner not found' };
            const cs = window.getComputedStyle(el);
            return {
                display: cs.display,
                flexDirection: cs.flexDirection,
                overflow: cs.overflow,
                height: cs.height,
                className: el.className,
                id: el.id,
            };
        }""")

        # 3. Computed styles for #wizardStep1
        wizard_step1 = page.evaluate("""() => {
            const el = document.getElementById('wizardStep1');
            if (!el) return { error: 'Element #wizardStep1 not found' };
            const cs = window.getComputedStyle(el);
            return {
                display: cs.display,
                minWidth: cs.minWidth,
                width: cs.width,
                flexShrink: cs.flexShrink,
                className: el.className,
            };
        }""")

        # 4. Parent check
        parent_check = page.evaluate("""() => {
            const el = document.getElementById('wizardSlides');
            if (!el) return { error: '#wizardSlides not found' };
            const parent = el.parentElement;
            return {
                parentClassName: parent ? parent.className : 'no parent',
                parentId: parent ? parent.id : 'no id',
                parentTagName: parent ? parent.tagName : 'none',
            };
        }""")

        # 5. All wizard-block elements visibility check
        all_steps = page.evaluate("""() => {
            const steps = document.querySelectorAll('.wizard-block');
            return Array.from(steps).map((el, i) => {
                const cs = window.getComputedStyle(el);
                const rect = el.getBoundingClientRect();
                return {
                    index: i,
                    id: el.id,
                    display: cs.display,
                    visibility: cs.visibility,
                    opacity: cs.opacity,
                    width: cs.width,
                    height: cs.height,
                    offsetTop: el.offsetTop,
                    boundingTop: rect.top,
                    boundingLeft: rect.left,
                };
            });
        }""")

        print("=== #wizardSlides computed styles ===")
        print(json.dumps(wizard_slides, indent=2))

        print("\n=== .wizard-inner computed styles ===")
        print(json.dumps(wizard_inner, indent=2))

        print("\n=== #wizardStep1 computed styles ===")
        print(json.dumps(wizard_step1, indent=2))

        print("\n=== Parent of #wizardSlides ===")
        print(json.dumps(parent_check, indent=2))

        print("\n=== All .wizard-block steps ===")
        print(json.dumps(all_steps, indent=2))

        # Full-page screenshot
        page.screenshot(
            path='/Users/emi/Documents/GitHub/energx-project/screenshots/wizard_full_page.png',
            full_page=True
        )
        print("\nFull-page screenshot saved.")

        browser.close()

inspect_wizard()
