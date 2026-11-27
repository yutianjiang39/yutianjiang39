"""Build the visual performance highlight for Multisource HL Copy.

Writes a light and a dark SVG into assets/. Figures come from the project's
published performance summary; each panel keeps its own scope in the footer.

    python tools/build_highlights.py
"""

from xml.sax.saxutils import escape

from build_diagrams import ASSETS, FONT, THEMES

W, H = 1200, 470
PANEL_Y, PANEL_H, PANEL_W = 84, 300, 357
PANEL_X = (40, 421, 802)


def build(theme):
    t = THEMES[theme]
    out = []

    def text(x, y, s, size=13, weight=400, fill="text", anchor="middle"):
        out.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" '
            f'fill="{t[fill]}" text-anchor="{anchor}">{escape(s)}</text>'
        )

    def caption(px, title):
        text(px + 24, PANEL_Y + PANEL_H - 24, title, 15, 600, "text", "start")

    # frame + header
    out.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{t["bg"]}" stroke="{t["frame"]}"/>')
    out.append(f'<rect x="40" y="33" width="4" height="14" rx="2" fill="{t["accent"]}"/>')
    text(54, 45, "MULTISOURCE HL COPY", 12, 700, "accent", "start")
    text(232, 45, "Performance · 性能", 12.5, 400, "muted", "start")

    for px in PANEL_X:
        out.append(
            f'<rect x="{px}" y="{PANEL_Y}" width="{PANEL_W}" height="{PANEL_H}" rx="12" '
            f'fill="{t["node"]}" stroke="{t["node_stroke"]}"/>'
        )

    # -- panel 1: latency scale -------------------------------------------------
    px = PANEL_X[0]
    text(px + 24, PANEL_Y + 92, "23", 64, 700, "text", "start")
    text(px + 104, PANEL_Y + 92, "ms p99", 20, 500, "accent", "start")
    x0, x1, ty = px + 30, px + PANEL_W - 30, PANEL_Y + 175
    scale = lambda ms: x0 + (x1 - x0) * ms / 30
    out.append(f'<rect x="{x0}" y="{ty - 5}" width="{x1 - x0}" height="10" rx="5" fill="{t["inner"]}" stroke="{t["node_stroke"]}"/>')
    out.append(f'<rect x="{x0}" y="{ty - 5}" width="{scale(23) - x0:.1f}" height="10" rx="5" fill="{t["accent_stroke"]}"/>')
    out.append(f'<rect x="{x0}" y="{ty - 5}" width="{scale(14) - x0:.1f}" height="10" rx="5" fill="{t["accent"]}"/>')
    for ms in (0, 10, 20, 30):
        text(scale(ms), ty + 30, f"{ms}", 11, 400, "muted")
    for ms, label, dy in ((14, "p50 14", -18), (23, "p99 23", -18)):
        out.append(f'<circle cx="{scale(ms):.1f}" cy="{ty}" r="7" fill="{t["bg"]}" stroke="{t["accent"]}" stroke-width="3"/>')
        text(scale(ms), ty + dy, label, 12, 600, "text")
    caption(px, "Local submit latency · 本地提交延迟")

    # -- panel 2: burst waveform ------------------------------------------------
    px = PANEL_X[1]
    text(px + 24, PANEL_Y + 92, "150", 64, 700, "text", "start")
    text(px + 142, PANEL_Y + 92, "signals/s", 20, 500, "accent", "start")
    bx0, bx1, base, top = px + 30, px + PANEL_W - 30, PANEL_Y + 215, PANEL_Y + 125
    seg = (bx1 - bx0) / 7
    pts = [(bx0, base)]
    for i in range(3):
        a = bx0 + seg * (2 * i + 0.5)
        b = a + seg
        pts += [(a, base), (a + 6, top), (b - 6, top), (b, base)]
    pts.append((bx1, base))
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = d + f" {bx1:.1f},{base} {bx0:.1f},{base}"
    out.append(f'<polygon points="{area}" fill="{t["accent_fill"]}"/>')
    out.append(f'<polyline points="{d}" fill="none" stroke="{t["accent"]}" stroke-width="2.5" stroke-linejoin="round"/>')
    out.append(f'<line x1="{bx0}" y1="{base}" x2="{bx1}" y2="{base}" stroke="{t["node_stroke"]}"/>')
    for i in range(3):
        text(bx0 + seg * (2 * i + 1), base + 22, "5 s", 11, 400, "muted")
    caption(px, "Two-source bursts · 双来源信号脉冲")

    # -- panel 3: fan-in of targets ---------------------------------------------
    px = PANEL_X[2]
    text(px + 24, PANEL_Y + 92, "8", 64, 700, "text", "start")
    text(px + 70, PANEL_Y + 92, "targets", 20, 500, "accent", "start")
    cx, cy = px + PANEL_W / 2 + 40, PANEL_Y + 175
    for i in range(8):
        sx, sy = px + 50, PANEL_Y + 120 + i * (110 / 7)
        out.append(f'<path d="M{sx + 7:.1f},{sy:.1f} C{sx + 90:.1f},{sy:.1f} {cx - 90:.1f},{cy} {cx - 26:.1f},{cy}" fill="none" stroke="{t["accent_stroke"]}" stroke-width="1.5"/>')
        out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="7" fill="{t["accent"]}"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="26" fill="{t["inner"]}" stroke="{t["accent"]}" stroke-width="3"/>')
    out.append(f'<path d="M{cx - 6},{cy - 11} L{cx + 10},{cy} L{cx - 6},{cy + 11} Z" fill="{t["accent"]}"/>')
    out.append(f'<line x1="{cx + 30}" y1="{cy}" x2="{cx + 92}" y2="{cy}" stroke="{t["line"]}" stroke-width="2"/>')
    out.append(f'<path d="M{cx + 92},{cy - 6} L{cx + 102},{cy} L{cx + 92},{cy + 6} Z" fill="{t["line"]}"/>')
    text(cx + 66, cy - 12, "HL", 12, 700, "muted")
    caption(px, "Multi-source following · 多来源跟随")

    # -- footer: scope of each figure -------------------------------------------
    text(40, H - 52, "p99: local submission, 1,765 mainnet orders  ·  Bursts: 3 × 5 s per run, 10 runs, not sustained  ·  8: configured limit  ·  3 targets ≈ 144 h live", 12, 400, "muted", "start")
    text(40, H - 30, "p99 仅为本地提交；脉冲为短时峰值，非持续吞吐；8 为配置上限；3 个目标约 144 小时实盘", 12, 400, "muted", "start")

    desc = (
        "Multisource HL Copy performance: local submission p99 23 ms and p50 14 ms over 1,765 mainnet orders; "
        "two-source signal bursts of 150 per second in three 5-second bursts per run; up to 8 configurable targets "
        "converging into one engine; 3 targets run about 144 hours live."
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-labelledby="title desc" font-family="{FONT}">\n'
        f'<title id="title">Multisource HL Copy · Performance · 性能</title>\n'
        f'<desc id="desc">{escape(desc)}</desc>\n' + "\n".join(out) + "\n</svg>\n"
    )


def main():
    for theme in THEMES:
        path = ASSETS / f"multisource-hl-copy-performance-{theme}.svg"
        path.write_text(build(theme), encoding="utf-8")
        print(f"wrote {path.relative_to(ASSETS.parent)}")


if __name__ == "__main__":
    main()
