"""Build the visual performance highlight for Multisource HL Copy.

One left-to-right flow: sources fan into the engine, the engine submits to
Hyperliquid, and each figure sits on the part of the flow it describes.
Writes a light and a dark SVG into assets/. Figures come from the project's
published performance summary; their scope is stated in the footer.

    python tools/build_highlights.py
"""

from xml.sax.saxutils import escape

from build_diagrams import ASSETS, FONT, THEMES

W, H = 1200, 520

EXTRA = {
    "light": {"glow": "#3FB8AF", "hi": "#1B7F79", "dot": "#D8DEE4"},
    "dark": {"glow": "#3FB8AF", "hi": "#7CE0D6", "dot": "#21262D"},
}

SRC_X = 150
SRC_Y = [228 + i * 24 for i in range(8)]
ENG = (640, 312)
HL_X = 1010


def bezier(p0, p1, p2, p3, s):
    u = 1 - s
    return tuple(u**3 * a + 3 * u * u * s * b + 3 * u * s * s * c + s**3 * d for a, b, c, d in zip(p0, p1, p2, p3))


def build(theme):
    t = {**THEMES[theme], **EXTRA[theme]}
    out = []

    def text(x, y, s, size=13, weight=400, fill="text", anchor="middle", extra=""):
        colour = fill if fill.startswith("url(") else t[fill]
        out.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" '
            f'fill="{colour}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'
        )

    def metric(cx, value, unit, label):
        out.append(
            f'<text x="{cx}" y="150" text-anchor="middle" font-weight="800" fill="url(#num)" letter-spacing="-2">'
            f'<tspan font-size="64">{escape(value)}</tspan>'
            f'<tspan font-size="20" font-weight="600" fill="{t["accent"]}" dx="8" letter-spacing="0">{escape(unit)}</tspan></text>'
        )
        text(cx, 180, label, 14, 500, "muted")

    defs = (
        f'<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1.2" fill="{t["dot"]}"/></pattern>'
        f'<linearGradient id="num" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{t["text"]}"/><stop offset="1" stop-color="{t["hi"]}"/></linearGradient>'
        f'<linearGradient id="wire" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{t["glow"]}" stop-opacity="0.2"/><stop offset="1" stop-color="{t["glow"]}" stop-opacity="0.85"/></linearGradient>'
        f'<radialGradient id="halo"><stop offset="0" stop-color="{t["glow"]}" stop-opacity="0.4"/>'
        f'<stop offset="1" stop-color="{t["glow"]}" stop-opacity="0"/></radialGradient>'
        f'<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>'
        f'<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
        f'<path d="M0,0 L10,5 L0,10 Z" fill="{t["accent"]}"/></marker>'
    )

    # canvas
    out.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="{t["bg"]}" stroke="{t["frame"]}"/>')
    out.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="url(#grid)" opacity="0.9"/>')
    out.append(f'<rect x="40" y="38" width="4" height="18" rx="2" fill="{t["accent"]}"/>')
    text(54, 53, "MULTISOURCE HL COPY", 13, 700, "accent", "start", ' letter-spacing="1.4"')
    text(W - 40, 53, "Performance · 性能", 13, 500, "muted", "end")

    # metrics, each above the part of the flow it describes
    metric(SRC_X, "8", "targets", "Sources followed · 跟随来源")
    metric(430, "150", "/ s", "Signal bursts · 信号脉冲")
    metric(825, "23", "ms p99", "Local submit · 本地提交")
    for x, y in ((SRC_X, SRC_Y[0] - 22), (430, 236), (825, ENG[1] - 30)):
        out.append(f'<line x1="{x}" y1="198" x2="{x}" y2="{y}" stroke="{t["accent_stroke"]}" stroke-dasharray="2 4"/>')

    # sources fanning into the engine, with signal packets in flight
    ex, ey = ENG
    for i, sy in enumerate(SRC_Y):
        p0, p1, p2, p3 = (SRC_X + 9, sy), (SRC_X + 200, sy), (ex - 220, ey), (ex - 46, ey)
        out.append(
            f'<path d="M{p0[0]},{p0[1]} C{p1[0]},{p1[1]} {p2[0]},{p2[1]} {p3[0]},{p3[1]}" '
            f'fill="none" stroke="url(#wire)" stroke-width="1.8"/>'
        )
        for s in (0.22 + 0.07 * (i % 3), 0.55 + 0.06 * ((i + 1) % 3)):
            x, y = bezier(p0, p1, p2, p3, s)
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{t["glow"]}" opacity="0.35" filter="url(#blur)"/>')
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{t["accent"]}"/>')
        out.append(f'<circle cx="{SRC_X}" cy="{sy}" r="9" fill="{t["inner"]}" stroke="{t["accent"]}" stroke-width="2.5"/>')
        out.append(f'<circle cx="{SRC_X}" cy="{sy}" r="3.5" fill="{t["accent"]}"/>')

    # engine
    out.append(f'<circle cx="{ex}" cy="{ey}" r="90" fill="url(#halo)"/>')
    out.append(f'<circle cx="{ex}" cy="{ey}" r="46" fill="{t["inner"]}" stroke="{t["accent"]}" stroke-width="4"/>')
    out.append(f'<path d="M{ex - 11},{ey - 18} L{ex + 18},{ey} L{ex - 11},{ey + 18} Z" fill="{t["accent"]}"/>')
    text(ex, ey + 78, "Execution engine · 执行引擎", 13, 600, "text")

    # engine -> Hyperliquid, with the latency span over the hop
    out.append(
        f'<line x1="{ex + 52}" y1="{ey}" x2="{HL_X - 8}" y2="{ey}" stroke="{t["accent"]}" stroke-width="3" marker-end="url(#arrow)"/>'
    )
    a, b = ex + 60, HL_X - 20
    out.append(
        f'<path d="M{a},{ey - 18} L{a},{ey - 28} L{b},{ey - 28} L{b},{ey - 18}" fill="none" stroke="{t["accent_stroke"]}" stroke-width="1.5"/>'
    )
    text((a + b) / 2, ey + 30, "p50 14 ms  ·  p99 23 ms", 12, 600, "muted")
    out.append(f'<rect x="{HL_X}" y="{ey - 32}" width="150" height="64" rx="32" fill="{t["accent"]}"/>')
    text(HL_X + 75, ey + 7, "Hyperliquid", 18, 800, "bg")

    # footer: scope of each figure
    out.append(f'<line x1="40" y1="{H - 76}" x2="{W - 40}" y2="{H - 76}" stroke="{t["frame"]}"/>')
    text(40, H - 48, "8: configured limit  ·  150/s: 3 × 5 s bursts per run, 10 runs, not sustained  ·  23 ms: local submission p99, 1,765 mainnet orders  ·  3 targets ≈ 144 h live", 11.5, 400, "muted", "start")
    text(40, H - 27, "8 为配置上限；150/s 为短时脉冲，非持续吞吐；23 ms 为本地提交 p99；3 个目标约 144 小时实盘", 11.5, 400, "muted", "start")

    desc = (
        "Multisource HL Copy as one flow: up to 8 sources fan into the execution engine with signal bursts of "
        "150 per second, and the engine submits to Hyperliquid with local submission latency of p50 14 ms and "
        "p99 23 ms over 1,765 mainnet orders. 3 targets have run about 144 hours live."
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-labelledby="title desc" font-family="{FONT}">\n'
        f'<title id="title">Multisource HL Copy · Performance · 性能</title>\n'
        f'<desc id="desc">{escape(desc)}</desc>\n'
        f'<defs>{defs}</defs>\n' + "\n".join(out) + "\n</svg>\n"
    )


def main():
    for theme in THEMES:
        path = ASSETS / f"multisource-hl-copy-performance-{theme}.svg"
        path.write_text(build(theme), encoding="utf-8")
        print(f"wrote {path.relative_to(ASSETS.parent)}")


if __name__ == "__main__":
    main()
