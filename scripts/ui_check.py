from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1680, "height": 1000})
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.goto("http://localhost:8000/", wait_until="networkidle")
    page.wait_for_timeout(3000)

    audit = page.evaluate(
        """() => {
      const els = [...document.querySelectorAll('div')];
      const files = els.find(d => d.textContent.trim() === '2310');
      const risk = els.find(d => d.className.includes('text-3xl'));
      return {
        filesCard: files ? files.textContent : null,
        risk: risk ? risk.textContent.trim() : null,
        flagCards: document.querySelectorAll('main button.block.w-full').length,
        timelineItems: document.querySelectorAll('.tl-item').length,
        overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth,
      };
    }"""
    )
    print("audit:", audit)
    page.screenshot(path="/home/user/acpia/docs/screenshot_dashboard.png")

    # graph tab at 2.4k nodes
    t0 = page.evaluate("() => performance.now()")
    page.click("text=Open graph view")
    page.wait_for_timeout(3500)
    t1 = page.evaluate("() => performance.now()")
    svg = page.evaluate(
        "() => { const s = document.querySelector('svg'); "
        "return s ? { circles: s.querySelectorAll('circle').length, lines: s.querySelectorAll('line').length } : null; }"
    )
    print(f"graph opened in {(t1-t0)/1000:.1f}s:", svg)
    page.screenshot(path="/home/user/acpia/docs/screenshot_graph.png")

    # query still works
    page.click(".fixed.inset-0.z-40 button:has-text('Back to console')")
    page.wait_for_timeout(600)
    page.fill("input[placeholder*='plain English']", "Who was the most active contact at night?")
    page.click("button:has-text('Ask')")
    page.wait_for_timeout(2500)
    ok = page.evaluate(
        "() => document.body.textContent.includes('Most active contact') && document.body.textContent.includes('Manoj P')"
    )
    print("query works:", ok)
    page.screenshot(path="/home/user/acpia/docs/screenshot_query.png")
    print("console errors:", errors[:3] if errors else "none")
    b.close()
print("done")
