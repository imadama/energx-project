from playwright.sync_api import sync_playwright

def sample_colors(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        page.goto(url, wait_until='networkidle')

        # Sample computed styles for key elements
        results = page.evaluate("""() => {
            const hero = document.querySelector('.hero') || document.querySelector('section.hero') || document.querySelector('[class*="hero"]');
            const h1 = document.querySelector('h1');
            const ghostBtn = Array.from(document.querySelectorAll('a, button')).find(el => el.textContent.trim().includes('Hoe werkt het'));
            const ctaSection = document.querySelector('.cta-section') || document.querySelector('[class*="cta"]') || document.querySelector('[class*="offerte"]');

            const getStyle = (el) => {
                if (!el) return null;
                const cs = window.getComputedStyle(el);
                return {
                    tagName: el.tagName,
                    className: el.className,
                    id: el.id,
                    backgroundColor: cs.backgroundColor,
                    color: cs.color,
                    backgroundImage: cs.backgroundImage,
                    border: cs.border,
                    outline: cs.outline,
                    text: el.textContent.trim().substring(0, 80)
                };
            };

            // Also get the hero background by looking at the first section or the body of the hero area
            const sections = Array.from(document.querySelectorAll('section'));
            const firstSection = sections[0];

            return {
                hero: getStyle(hero),
                firstSection: getStyle(firstSection),
                h1: getStyle(h1),
                ghostBtn: getStyle(ghostBtn),
                ctaSection: getStyle(ctaSection),
                allSectionClasses: sections.map(s => ({cls: s.className, id: s.id})),
                allCtaLike: Array.from(document.querySelectorAll('[class*="cta"], [class*="offerte"], [class*="banner"]')).map(el => ({
                    tag: el.tagName, cls: el.className, bg: window.getComputedStyle(el).backgroundColor, color: window.getComputedStyle(el).color, bgImg: window.getComputedStyle(el).backgroundImage
                })).slice(0, 5)
            };
        }""")

        import json
        print(json.dumps(results, indent=2))
        browser.close()

sample_colors('http://localhost:5173/')
