from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1680, "height": 1000})
    nan_edges = []
    page.on("console", lambda m: nan_edges.append(m.text) if m.type == "error" else None)
    page.goto("http://localhost:8000/", wait_until="networkidle")
    page.wait_for_timeout(2500)
    page.click("text=Open graph view")
    page.wait_for_timeout(6000)
    print("errors:", nan_edges[:4])
    # inspect DOM for NaN lines
    info = page.evaluate(
        """() => {
      const lines = [...document.querySelectorAll('line')];
      const bad = lines.filter(l => ['x1','y1','x2','y2'].some(a => l.getAttribute(a) === 'NaN' || isNaN(l.getAttribute(a))));
      const groups = [...document.querySelectorAll('svg g')];
      return {
        badLineCount: bad.length,
        sample: bad.slice(0,3).map(l => ({x1:l.getAttribute('x1'), y1:l.getAttribute('y1')})),
        groupCount: groups.length,
      };
    }"""
    )
    print("dom info:", info)
    b.close()
