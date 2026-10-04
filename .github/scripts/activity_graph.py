"""Draw the last 31 days of contributions as an SVG area chart (replaces the dead activity-graph service)."""
import json, os, sys, urllib.request

USER, OUT, DAYS = "TusharDwarka", "activity-graph.svg", 31
W, H, L, R, T, B = 1000, 300, 50, 20, 50, 40

def fetch():
    q = '{user(login:"%s"){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}' % USER
    req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": q}).encode(),
                                 {"Authorization": "bearer " + os.environ["GITHUB_TOKEN"]})
    weeks = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [(d["date"], d["contributionCount"]) for w in weeks for d in w["contributionDays"]][-DAYS:]

def svg(days):
    top = max(4, max(c for _, c in days))
    x = lambda i: L + i * (W - L - R) / (len(days) - 1)
    y = lambda c: H - B - c * (H - T - B) / top
    pts = " ".join(f"{x(i):.1f},{y(c):.1f}" for i, (_, c) in enumerate(days))
    grid = "".join(f'<line x1="{L}" x2="{W-R}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="#2a2e45"/>'
                   f'<text x="{L-10}" y="{y(v)+4:.1f}" text-anchor="end" class="s">{v}</text>'
                   for v in sorted({0, top // 4, top // 2, 3 * top // 4, top}))
    labels = "".join(f'<text x="{x(i):.1f}" y="{H-B+20}" text-anchor="middle" class="s">{d[8:]}</text>'
                     for i, (d, _) in enumerate(days) if i % 3 == 0)
    dots = "".join(f'<circle cx="{x(i):.1f}" cy="{y(c):.1f}" r="3.5" fill="#bf91f3"><title>{d}: {c}</title></circle>'
                   for i, (d, c) in enumerate(days))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>.s{{font:12px 'Segoe UI',Ubuntu,sans-serif;fill:#a9b1d6}}.t{{font:600 18px 'Segoe UI',Ubuntu,sans-serif;fill:#70a5fd}}</style>
<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#70a5fd" stop-opacity=".45"/><stop offset="1" stop-color="#70a5fd" stop-opacity="0"/></linearGradient></defs>
<rect width="{W}" height="{H}" rx="16" fill="#1a1b27"/>
<text x="{W/2}" y="32" text-anchor="middle" class="t">{USER}'s Contribution Graph · last {DAYS} days</text>
{grid}{labels}
<polygon points="{x(0):.1f},{H-B} {pts} {x(len(days)-1):.1f},{H-B}" fill="url(#g)"/>
<polyline points="{pts}" fill="none" stroke="#70a5fd" stroke-width="2.5" stroke-linejoin="round"/>
{dots}
</svg>'''

if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:  # no network: render a fake month and check it parses
        import xml.dom.minidom
        xml.dom.minidom.parseString(svg([(f"2026-01-{i+1:02d}", i % 7) for i in range(DAYS)]))
        print("selftest ok"); sys.exit()
    open(OUT, "w", encoding="utf-8").write(svg(fetch()))
